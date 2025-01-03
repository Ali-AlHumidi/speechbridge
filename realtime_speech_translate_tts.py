import os
from google.cloud import speech
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech
import pyaudio
import tempfile
import simpleaudio as sa  # For playing audio

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_CREDENTIALS_PATH")

# Audio recording parameters
CHUNK = 1024  # Size of each audio chunk
FORMAT = pyaudio.paInt16  # Format of audio
CHANNELS = 1  # Mono audio
RATE = 16000  # 16kHz sample rate


def stream_audio_to_text_translate_tts(target_language):
    """
    Streams microphone audio to Google Cloud Speech-to-Text API for real-time transcription,
    translates the transcription, and converts it to speech in the target language.
    """
    # Initialize clients
    speech_client = speech.SpeechClient()
    translate_client = translate.Client()
    tts_client = texttospeech.TextToSpeechClient()

    # Configure microphone stream
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    # Google API Streaming configuration
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="en-US",
    )
    streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

    print("Listening, translating, and synthesizing speech (press Ctrl+C to stop)...")

    # Generator function to yield audio chunks
    def generate_audio():
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            yield speech.StreamingRecognizeRequest(audio_content=data)

    # Use Google's streaming API for real-time transcription
    try:
        responses = speech_client.streaming_recognize(config=streaming_config, requests=generate_audio())

        for response in responses:
            for result in response.results:
                if result.is_final:
                    # Step 1: Get the final transcription
                    transcript = result.alternatives[0].transcript
                    print(f"Transcript: {transcript}")

                    # Step 2: Translate the transcription
                    translation = translate_client.translate(transcript, target_language=target_language)
                    translated_text = translation['translatedText']
                    print(f"Translated Text ({target_language}): {translated_text}")

                    # Step 3: Convert the translated text to speech
                    synthesis_input = texttospeech.SynthesisInput(text=translated_text)

                    # Configure the voice settings
                    voice = texttospeech.VoiceSelectionParams(
                        language_code=target_language,
                        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
                    )
                    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

                    # Generate speech audio
                    response = tts_client.synthesize_speech(
                        input=synthesis_input, voice=voice, audio_config=audio_config
                    )

                    # Save the audio to a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                        temp_audio.write(response.audio_content)
                        temp_audio.flush()

                        # Play the audio
                        wave_obj = sa.WaveObject.from_wave_file(temp_audio.name)
                        play_obj = wave_obj.play()
                        play_obj.wait_done()  # Wait for playback to finish

    except KeyboardInterrupt:
        print("Stopped listening.")

    finally:
        # Clean up
        stream.stop_stream()
        stream.close()
        audio.terminate()


if __name__ == "__main__":
    # Set target language for translation (e.g., "es" for Spanish, "fr" for French)
    target_language_code = "es"  # Change this to the desired target language code
    stream_audio_to_text_translate_tts(target_language_code)
