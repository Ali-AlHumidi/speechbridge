import os
from google.cloud import speech

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_CREDENTIALS_PATH")

# Speech-to-Text
def transcribe_audio(file_path):
    client = speech.SpeechClient()

    # Read the audio file
    with open(file_path, "rb") as audio_file:
        content = audio_file.read()

    # Configure the audio and recognition settings
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Send the audio to Google Cloud for transcription
    response = client.recognize(config=config, audio=audio)

    # Print the transcription results
    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")
        return result.alternatives[0].transcript


# Main Functionality
if __name__ == "__main__":
    # Transcribe the audio file
    transcript = transcribe_audio("test_audio.wav")
    print(f"Transcribed Text: {transcript}")
