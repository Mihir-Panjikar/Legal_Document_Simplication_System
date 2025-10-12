import ollama
import streamlit as st
import asyncio
from utils.ollama_config import OLLAMA_API_HOST


async def translate_text(text, src="en", dest="hi"):
    """
    Translates text using Ollama.

    Args:
        text (str): Text to translate
        src (str): Source language code
        dest (str): Destination language code

    Returns:
        str: Translated text
    """
    # Map language codes to full names for better model understanding
    language_map = {
        "hi": "Hindi",
        "mr": "Marathi",
        "en": "English"
    }

    target_language = language_map.get(dest, dest)

    try:
        # Set up the client
        client = ollama.Client(host=OLLAMA_API_HOST)

        # Prepare prompt for translation
        prompt = f"""Translate the following text from English to {target_language}.
        Maintain the meaning, tone, and style as much as possible.
        Only return the translated text, without any additional explanations.
        
        Text to translate:
        {text}
        """

        # Use a more capable model for translation
        model = "llama3"  # Llama3 is typically better at multilingual tasks

        response = client.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.2  # Slightly higher temperature for translation
            }
        )

        translated_text = response["message"]["content"]

        # Clean up any prefixes the model might add
        prefixes = [
            f"Here's the translation to {target_language}:",
            f"Translation to {target_language}:",
            f"{target_language} translation:",
            f"Translated text in {target_language}:"
        ]

        for prefix in prefixes:
            if translated_text.startswith(prefix):
                translated_text = translated_text[len(prefix):].strip()

        return translated_text

    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return f"Error in translation: {str(e)}"


def translate_with_retries(text, target_language, max_retries=3, retry_delay=2):
    """Attempt translation with retries on connection errors"""
    import time

    for attempt in range(max_retries):
        try:
            # Map language codes to full names for better model understanding
            language_map = {
                "hi": "Hindi",
                "mr": "Marathi",
                "en": "English"
            }

            target_language_full = language_map.get(
                target_language, target_language)

            # Set up the client
            client = ollama.Client(host=OLLAMA_API_HOST)

            # Prepare prompt for translation
            prompt = f"""Translate the following text from English to {target_language_full}.
            Maintain the meaning, tone, and style as much as possible.
            Only return the translated text, without any additional explanations.
            
            Text to translate:
            {text}
            """

            # Use a more capable model for translation
            model = "llama3"  # Llama3 is typically better at multilingual tasks

            response = client.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.2  # Slightly higher temperature for translation
                }
            )

            translated_text = response["message"]["content"]

            # Clean up any prefixes the model might add
            prefixes = [
                f"Here's the translation to {target_language_full}:",
                f"Translation to {target_language_full}:",
                f"{target_language_full} translation:",
                f"Translated text in {target_language_full}:"
            ]

            for prefix in prefixes:
                if translated_text.startswith(prefix):
                    translated_text = translated_text[len(prefix):].strip()

            return translated_text

        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(
                    f"Connection attempt {attempt+1} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                st.error(
                    f"Failed to connect to Ollama after {max_retries} attempts. Error: {str(e)}")
                return None
