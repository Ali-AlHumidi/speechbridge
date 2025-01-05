import os
import pyaudio
import wave
import sounddevice as sd
import numpy as np
from google.cloud import speech
from google.cloud import texttospeech
from google.cloud import translate_v2 as translate
import tempfile

# Ensure the Google credentials are set
if not os.getenv("GOOGLE_CREDENTIALS_PATH"):
    raise EnvironmentError("GOOGLE_CREDENTIALS_PATH environment variable is not set.")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_CREDENTIALS_PATH")

# Audio recording settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

def play_audio_to_virtual_mic(audio_file):
    """
    Play synthesized audio through the virtual microphone (BlackHole).
    """
    with wave.open(audio_file, 'rb') as wf:
        data = wf.readframes(wf.getnframes())
        audio_data = np.frombuffer(data, dtype=np.int16)
        sd.play(audio_data, samplerate=wf.getframerate(), blocking=True)

def stream_audio_to_text_translate_tts(target_language):
    """
    Streams microphone audio to Google Cloud APIs for transcription, translation, and text-to-speech.
    """
    # Initialize Google Cloud clients
    speech_client = speech.SpeechClient()
    translate_client = translate.Client()
    tts_client = texttospeech.TextToSpeechClient()

    # Set up microphone input
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    # Configure Google Speech-to-Text streaming
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="en-US",
    )
    streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

    print("Listening, translating, and synthesizing speech (press Ctrl+C to stop)...")

    def generate_audio():
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            yield speech.StreamingRecognizeRequest(audio_content=data)

    try:
        responses = speech_client.streaming_recognize(config=streaming_config, requests=generate_audio())

        for response in responses:
            for result in response.results:
                if result.is_final:
                    # Transcription
                    transcript = result.alternatives[0].transcript
                    print(f"Transcript: {transcript}")

                    # Translation
                    translation = translate_client.translate(transcript, target_language=target_language)
                    translated_text = translation['translatedText']
                    print(f"Translated Text ({target_language}): {translated_text}")

                    # Text-to-Speech
                    synthesis_input = texttospeech.SynthesisInput(text=translated_text)
                    voice = texttospeech.VoiceSelectionParams(
                        language_code=target_language,
                        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
                    )
                    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

                    response = tts_client.synthesize_speech(
                        input=synthesis_input, voice=voice, audio_config=audio_config
                    )

                    # Save synthesized audio to a temporary file
                    with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_audio:
                        temp_audio.write(response.audio_content)
                        temp_audio.flush()

                        # Play the audio through BlackHole
                        play_audio_to_virtual_mic(temp_audio.name)

    except KeyboardInterrupt:
        print("Stopped listening.")

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    # Set your target language code (e.g., "es" for Spanish, "fr" for French)
    target_language_code = "es"
    stream_audio_to_text_translate_tts(target_language_code)
