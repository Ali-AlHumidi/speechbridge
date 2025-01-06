import os
import tkinter as tk
from tkinter import ttk
from threading import Thread
from google.cloud import speech, texttospeech, translate_v2 as translate
import pyaudio
import wave
import tempfile
import sounddevice as sd
import numpy as np

# Google Cloud setup
if not os.getenv("GOOGLE_CREDENTIALS_PATH"):
    raise EnvironmentError("GOOGLE_CREDENTIALS_PATH environment variable is not set.")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_CREDENTIALS_PATH")

# Audio recording settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Global flag to stop the process
running = False

def play_audio_to_virtual_mic(audio_file):
    """Play synthesized audio through the virtual microphone (BlackHole)."""
    with wave.open(audio_file, 'rb') as wf:
        data = wf.readframes(wf.getnframes())
        audio_data = np.frombuffer(data, dtype=np.int16)
        sd.play(audio_data, samplerate=wf.getframerate(), blocking=True)

def stream_audio_to_text_translate_tts(target_language, log_area):
    """Real-time transcription, translation, and text-to-speech."""
    global running
    running = True

    # Initialize Google Cloud clients
    speech_client = speech.SpeechClient()
    translate_client = translate.Client()
    tts_client = texttospeech.TextToSpeechClient()

    # Setup microphone input
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    # Configure Google Speech-to-Text
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="en-US",
    )
    streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

    def generate_audio():
        while running:
            data = stream.read(CHUNK, exception_on_overflow=False)
            yield speech.StreamingRecognizeRequest(audio_content=data)

    try:
        responses = speech_client.streaming_recognize(config=streaming_config, requests=generate_audio())

        for response in responses:
            for result in response.results:
                if result.is_final:
                    transcript = result.alternatives[0].transcript
                    log_area.insert(tk.END, f"Transcript: {transcript}\n")
                    log_area.see(tk.END)

                    # Translate
                    translation = translate_client.translate(transcript, target_language=target_language)
                    translated_text = translation['translatedText']
                    log_area.insert(tk.END, f"Translated Text ({target_language}): {translated_text}\n")
                    log_area.see(tk.END)

                    # Text-to-Speech
                    synthesis_input = texttospeech.SynthesisInput(text=translated_text)
                    voice = texttospeech.VoiceSelectionParams(
                        language_code=target_language, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
                    )
                    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)
                    response = tts_client.synthesize_speech(
                        input=synthesis_input, voice=voice, audio_config=audio_config
                    )

                    with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_audio:
                        temp_audio.write(response.audio_content)
                        temp_audio.flush()
                        play_audio_to_virtual_mic(temp_audio.name)

    except Exception as e:
        log_area.insert(tk.END, f"Error: {e}\n")
        log_area.see(tk.END)
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        running = False

def start_translation(target_language, log_area, status_label):
    """Start the translation in a separate thread."""
    if not running:
        status_label.config(text="Listening...", fg="green")
        thread = Thread(target=stream_audio_to_text_translate_tts, args=(target_language, log_area))
        thread.daemon = True
        thread.start()

def stop_translation(log_area, status_label):
    """Stop the translation process."""
    global running
    running = False
    status_label.config(text="Stopped", fg="red")
    log_area.insert(tk.END, "Stopped listening.\n")
    log_area.see(tk.END)

# GUI setup
def create_gui():
    window = tk.Tk()
    window.title("Real-Time Translation App")
    window.geometry("600x400")

    # Status Label
    status_label = tk.Label(window, text="Stopped", fg="red", font=("Arial", 12, "bold"))
    status_label.pack(pady=5)

    # Dropdown for target language
    language_label = tk.Label(window, text="Select Target Language:")
    language_label.pack(pady=5)
    target_language_var = tk.StringVar(value="es")  # Default to Spanish
    language_dropdown = ttk.Combobox(window, textvariable=target_language_var, state="readonly")
    language_dropdown["values"] = ["es", "fr", "de", "zh", "ar"]  # Added Arabic (ar)
    language_dropdown.pack(pady=5)

    # Text area for logs
    log_area = tk.Text(window, height=15, width=70)
    log_area.pack(pady=5)

    # Start and Stop buttons
    start_button = tk.Button(window, text="Start", command=lambda: start_translation(target_language_var.get(), log_area, status_label))
    start_button.pack(side=tk.LEFT, padx=10, pady=10)

    stop_button = tk.Button(window, text="Stop", command=lambda: stop_translation(log_area, status_label))
    stop_button.pack(side=tk.RIGHT, padx=10, pady=10)

    window.mainloop()

if __name__ == "__main__":
    create_gui()
