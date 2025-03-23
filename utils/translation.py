from googletrans import Translator

async def translate_text(text: str, src: str, dest: str) -> str:
    translator = Translator()
    translated_text = await translator.translate(text, src=src, dest=dest)
    return translated_text.text