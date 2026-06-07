"""
CyberGuard AI X - Multilingual Translator
Supports English, Hindi, Gujarati detection and translation
"""

from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator

# Ensure reproducible language detection
DetectorFactory.seed = 0

LANGUAGE_MAP = {
    'en': 'English',
    'hi': 'Hindi',
    'gu': 'Gujarati',
    'unknown': 'Unknown'
}

SUPPORTED_LANGUAGES = ['en', 'hi', 'gu']


def detect_language(text: str) -> str:
    """Detect language of input text"""
    try:
        if not text or len(text.strip()) < 5:
            return 'en'
        lang = detect(text)
        # Map common variations
        if lang in SUPPORTED_LANGUAGES:
            return lang
        return 'en'  # Default to English
    except Exception:
        return 'en'


def translate_to_english(text: str, source_lang: str = None) -> dict:
    """
    Translate text to English if needed.
    Returns: { 'original': str, 'translated': str, 'language': str, 'language_name': str }
    """
    result = {
        'original': text,
        'translated': text,
        'language': 'en',
        'language_name': 'English',
        'translation_needed': False
    }

    try:
        # Detect language
        detected_lang = source_lang if source_lang else detect_language(text)
        result['language'] = detected_lang
        result['language_name'] = LANGUAGE_MAP.get(detected_lang, 'Unknown')

        if detected_lang != 'en':
            result['translation_needed'] = True
            translator = GoogleTranslator(source=detected_lang, target='en')
            translated = translator.translate(text)
            result['translated'] = translated if translated else text
        else:
            result['translated'] = text

    except Exception as e:
        # Fallback: use original text
        result['translated'] = text
        result['language'] = source_lang or 'en'
        result['error'] = str(e)

    return result


def get_supported_languages() -> dict:
    """Return dict of supported languages"""
    return LANGUAGE_MAP
