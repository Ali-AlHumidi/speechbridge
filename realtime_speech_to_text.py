import os
from google.cloud import speech
from google.cloud import translate_v2 as translate
import pyaudio

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/alialhumidi/Documents/real-time-translation-app/credentials.json"

# Audio recording parameters
CHUNK = 1024  # Size of each audio chunk
FORMAT = pyaudio.paInt16  # Format of audio
CHANNELS = 1  # Mono audio
RATE = 16000  # 16kHz sample rate


def stream_audio_to_text_and_translate(target_language):
    """
    Streams microphone audio to Google Cloud Speech-to-Text API for real-time transcription,
    and translates the transcription into the target language.
    """
    # Initialize clients
    speech_client = speech.SpeechClient()
    translate_client = translate.Client()

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

    print("Listening and translating (press Ctrl+C to stop)...")

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
                    # Get the final transcription
                    transcript = result.alternatives[0].transcript
                    print(f"Transcript: {transcript}")

                    # Translate the transcription
                    translation = translate_client.translate(transcript, target_language=target_language)
                    print(f"Translated Text ({target_language}): {translation['translatedText']}")

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
    stream_audio_to_text_and_translate(target_language_code)
