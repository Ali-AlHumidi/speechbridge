import os
from google.cloud import translate_v2 as translate

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/alialhumidi/Documents/real-time-translation-app/credentials.json"

# Translate Text
def translate_text(text, target_language):
    """
    Translate the given text into the target language.

    Args:
        text (str): The text to translate.
        target_language (str): The language code of the target language (e.g., "es" for Spanish, "fr" for French).

    Returns:
        str: The translated text.
    """
    client = translate.Client()
    translation = client.translate(text, target_language=target_language)
    return translation['translatedText']


# Main Functionality
if __name__ == "__main__":
    # Example input text to translate
    text_to_translate = "Hello, how are you?"
    target_language_code = "es"  # Spanish

    # Translate the text
    translated_text = translate_text(text_to_translate, target_language_code)
    print(f"Translated Text: {translated_text}")
