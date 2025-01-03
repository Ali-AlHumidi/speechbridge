import os
from google.cloud import speech
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech
import pyaudio
import wave

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/alialhumidi/Documents/real-time-translation-app/credentials.json"

# 1. Record Audio
def record_audio(output_filename):
    """
    Records audio for 5 seconds and saves it to the specified file.
    """
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))


# 2. Speech-to-Text
def transcribe_audio(file_path):
    """
    Transcribes the audio file using Google Cloud Speech-to-Text API.
    """
    client = speech.SpeechClient()

    with open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")
        return result.alternatives[0].transcript


# 3. Translate Text
def translate_text(text, target_language):
    """
    Translates the given text into the target language using Google Cloud Translation API.
    """
    client = translate.Client()
    translation = client.translate(text, target_language=target_language)
    print(f"Translated Text: {translation['translatedText']}")
    return translation['translatedText']


# 4. Text-to-Speech
def text_to_speech(text, output_file):
    """
    Converts the given text to speech and saves it to an audio file using Google Cloud Text-to-Speech API.
    """
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="es-ES",  # Change this to match the target language
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio content written to {output_file}")


# Main Functionality
if __name__ == "__main__":
    # Step 1: Record Audio
    audio_file = "test_audio.wav"
    record_audio(audio_file)

    # Step 2: Transcribe the Audio
    transcript = transcribe_audio(audio_file)
    print(f"Transcribed Text: {transcript}")

    # Step 3: Translate the Transcription
    target_language = "es"  # Change to desired language code (e.g., "fr" for French, "de" for German)
    translated_text = translate_text(transcript, target_language)
    print(f"Translated Text: {translated_text}")

    # Step 4: Convert Translated Text to Speech
    output_audio_file = "output.mp3"
    text_to_speech(translated_text, output_audio_file)
    print(f"Translated speech saved to {output_audio_file}")
