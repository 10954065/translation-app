"""Canonical list of languages supported end-to-end by the translation backend.

Every entry's `code` must be a valid deep-translator / Google Translate language
code. The frontend fetches this list from GET /api/languages so the UI never
advertises a language the backend cannot actually translate.
"""

SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English", "nativeName": "English"},
    {"code": "fr", "name": "French", "nativeName": "Français"},
    {"code": "de", "name": "German", "nativeName": "Deutsch"},
    {"code": "es", "name": "Spanish", "nativeName": "Español"},
    {"code": "pt", "name": "Portuguese", "nativeName": "Português"},
    {"code": "it", "name": "Italian", "nativeName": "Italiano"},
    {"code": "nl", "name": "Dutch", "nativeName": "Nederlands"},
    {"code": "sv", "name": "Swedish", "nativeName": "Svenska"},
    {"code": "ar", "name": "Arabic", "nativeName": "العربية"},
    {"code": "zh-CN", "name": "Chinese (Simplified)", "nativeName": "中文"},
    {"code": "ja", "name": "Japanese", "nativeName": "日本語"},
    {"code": "ko", "name": "Korean", "nativeName": "한국어"},
    {"code": "hi", "name": "Hindi", "nativeName": "हिन्दी"},
    {"code": "ak", "name": "Twi", "nativeName": "Twi"},
    {"code": "ee", "name": "Ewe", "nativeName": "Eʋegbe"},
]

SUPPORTED_LANGUAGE_CODES = {lang["code"] for lang in SUPPORTED_LANGUAGES}


def is_supported_language(code: str) -> bool:
    return code in SUPPORTED_LANGUAGE_CODES
