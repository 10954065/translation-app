"""Translation abstraction.

Provider order is DeepL, then Google, then MyMemory. DeepL is optional
(requires DEEPL_API_KEY) but authenticated, so it is unaffected by the
datacenter-IP rate limiting that blocks Google's and MyMemory's free,
keyless, scraping-based endpoints on shared cloud hosts - the same class of
IP-based blocking the academic reference implementation's `googletrans`
library is also subject to. DeepL only covers a subset of
app.utils.languages.SUPPORTED_LANGUAGES, so Google and MyMemory remain as
fallback for languages it doesn't support (or if no key is configured).
Callers never import deep-translator directly - only this file would change
to swap in another provider.
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass

from deep_translator import DeeplTranslator, GoogleTranslator, MyMemoryTranslator
from deep_translator.exceptions import LanguageNotSupportedException, NotValidPayload

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="translate")

# deep-translator's GoogleTranslator uses plain ISO codes (en, fr, zh-CN, ...)
# but MyMemoryTranslator requires locale-tagged codes. Only languages in
# app.utils.languages.SUPPORTED_LANGUAGES need an entry here.
_MYMEMORY_LOCALE = {
    "en": "en-GB",
    "fr": "fr-FR",
    "de": "de-DE",
    "es": "es-ES",
    "pt": "pt-PT",
    "it": "it-IT",
    "nl": "nl-NL",
    "sv": "sv-SE",
    "ar": "ar-SA",
    "zh-CN": "zh-CN",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "hi": "hi-IN",
    "ak": "tw-GH",
    "ee": "ee-GH",
}

# DeepL is authenticated (a real API key, not a shared/anonymous scraping
# endpoint) so it is unaffected by the datacenter-IP rate limiting that
# blocks Google and MyMemory on cloud hosts. It only covers a subset of
# app.utils.languages.SUPPORTED_LANGUAGES though - no Arabic, Korean, Hindi,
# Twi, or Ewe - so it is tried first where available and the other
# providers remain as fallback for everything else.
_DEEPL_LOCALE = {
    "en": "en",
    "fr": "fr",
    "de": "de",
    "es": "es",
    "pt": "pt",
    "it": "it",
    "nl": "nl",
    "sv": "sv",
    "zh-CN": "zh",
    "ja": "ja",
}

# Small in-memory cache so identical text -> language pairs (common with
# repeated demo phrases, or the same PDF page requested twice) skip the
# network round trip.
_CACHE_MAX_ENTRIES = 500
_cache: dict[tuple[str, str], str] = {}
_cache_order: list[tuple[str, str]] = []


class TranslationError(Exception):
    """Raised when translation cannot be completed after retries."""


@dataclass
class TranslationResult:
    text: str
    source_language: str
    target_language: str
    ok: bool
    fallback_used: bool = False


def _cache_get(key: tuple[str, str]) -> str | None:
    return _cache.get(key)


def _cache_put(key: tuple[str, str], value: str) -> None:
    if key in _cache:
        return
    if len(_cache_order) >= _CACHE_MAX_ENTRIES:
        oldest = _cache_order.pop(0)
        _cache.pop(oldest, None)
    _cache[key] = value
    _cache_order.append(key)


class TranslationService:
    def __init__(self, timeout_seconds: float = 6.0, max_retries: int = 2, deepl_api_key: str = ""):
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.deepl_api_key = deepl_api_key

    def detect_language(self, text: str, default: str = "en") -> str:
        """Best-effort source language detection.

        deep-translator's GoogleTranslator has no standalone detect call, so
        we translate to English and read back the detected source language
        that the API reports. Falls back to `default` on any failure -
        MyMemory has no detection capability, so there is no fallback
        provider for this step.
        """
        try:
            translator = GoogleTranslator(source="auto", target="en")
            self._run_with_timeout(translator.translate, text)
            detected = getattr(translator, "_source", None) or getattr(translator, "source", None)
            if detected and detected != "auto":
                return detected
        except Exception as exc:  # noqa: BLE001 - external service, never crash the caller
            logger.warning("Language detection failed, defaulting to %s: %s", default, exc)
        return default

    def translate(self, text: str, target_language: str, source_language: str) -> TranslationResult:
        """Translate `text` from `source_language` to `target_language`.

        `source_language` must be a concrete language code, not "auto" - call
        `detect_language` first if the source is unknown. This keeps the
        MyMemory fallback usable, since that provider cannot auto-detect.
        """
        if not text.strip():
            return TranslationResult(text=text, source_language=source_language, target_language=target_language, ok=True)

        if source_language == target_language:
            return TranslationResult(text=text, source_language=source_language, target_language=target_language, ok=True)

        cache_key = (f"{source_language}:{text}", target_language)
        cached = _cache_get(cache_key)
        if cached is not None:
            return TranslationResult(text=cached, source_language=source_language, target_language=target_language, ok=True)

        providers = [self._translate_with_google, self._translate_with_mymemory]
        if self.deepl_api_key:
            providers.insert(0, self._translate_with_deepl)

        translated = None
        fallback_used = False
        for index, provider in enumerate(providers):
            translated = provider(text, source_language, target_language)
            if translated is not None:
                fallback_used = index > 0
                break

        if translated is not None:
            _cache_put(cache_key, translated)
            return TranslationResult(
                text=translated,
                source_language=source_language,
                target_language=target_language,
                ok=True,
                fallback_used=fallback_used,
            )

        logger.error("Translation failed on all providers (%s -> %s)", source_language, target_language)
        return TranslationResult(
            text=text,
            source_language=source_language,
            target_language=target_language,
            ok=False,
            fallback_used=True,
        )

    def translate_for_members(self, text: str, source_language: str, members: list[dict]) -> dict[str, TranslationResult]:
        """Translate `text` once per distinct target language among members.

        `members` is a list of {"id": ..., "language": ...}. Returns a map of
        member id -> TranslationResult so identical target languages are only
        translated once even with many participants.
        """
        distinct_targets = {m["language"] for m in members}
        by_language: dict[str, TranslationResult] = {}
        for target in distinct_targets:
            by_language[target] = self.translate(text, target, source_language)

        return {member["id"]: by_language[member["language"]] for member in members}

    # -- providers ---------------------------------------------------------

    def _translate_with_deepl(self, text: str, source_language: str, target_language: str) -> str | None:
        if not self.deepl_api_key:
            return None
        source_locale = _DEEPL_LOCALE.get(source_language)
        target_locale = _DEEPL_LOCALE.get(target_language)
        if not source_locale or not target_locale:
            return None

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                translator = DeeplTranslator(source=source_locale, target=target_locale, api_key=self.deepl_api_key)
                translated = self._run_with_timeout(translator.translate, text)
                if translated:
                    return translated
                last_error = TranslationError("Empty translation response")
            except (LanguageNotSupportedException, NotValidPayload) as exc:
                logger.error("DeepL translation rejected (%s -> %s): %s", source_language, target_language, exc)
                return None
            except Exception as exc:  # noqa: BLE001 - external network dependency
                last_error = exc
                logger.warning(
                    "DeepL translation attempt %d/%d failed (%s -> %s): %s",
                    attempt + 1,
                    self.max_retries + 1,
                    source_language,
                    target_language,
                    exc,
                )
                time.sleep(0.2 * (attempt + 1))
        logger.warning("DeepL translation exhausted retries (%s -> %s): %s", source_language, target_language, last_error)
        return None

    def _translate_with_google(self, text: str, source_language: str, target_language: str) -> str | None:
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                translator = GoogleTranslator(source=source_language, target=target_language)
                translated = self._run_with_timeout(translator.translate, text)
                if translated:
                    return translated
                last_error = TranslationError("Empty translation response")
            except (LanguageNotSupportedException, NotValidPayload) as exc:
                logger.error("Google translation rejected (%s -> %s): %s", source_language, target_language, exc)
                return None
            except Exception as exc:  # noqa: BLE001 - external network dependency
                last_error = exc
                logger.warning(
                    "Google translation attempt %d/%d failed (%s -> %s): %s",
                    attempt + 1,
                    self.max_retries + 1,
                    source_language,
                    target_language,
                    exc,
                )
                time.sleep(0.2 * (attempt + 1))
        logger.warning("Google translation exhausted retries (%s -> %s): %s", source_language, target_language, last_error)
        return None

    def _translate_with_mymemory(self, text: str, source_language: str, target_language: str) -> str | None:
        source_locale = _MYMEMORY_LOCALE.get(source_language)
        target_locale = _MYMEMORY_LOCALE.get(target_language)
        if not source_locale or not target_locale:
            return None
        try:
            translator = MyMemoryTranslator(source=source_locale, target=target_locale)
            translated = self._run_with_timeout(translator.translate, text)
            if translated:
                logger.info("MyMemory fallback succeeded (%s -> %s)", source_language, target_language)
            return translated or None
        except Exception as exc:  # noqa: BLE001 - external network dependency
            logger.warning("MyMemory fallback failed (%s -> %s): %s", source_language, target_language, exc)
            return None

    def _run_with_timeout(self, func, *args):
        future = _executor.submit(func, *args)
        try:
            return future.result(timeout=self.timeout_seconds)
        except FutureTimeoutError as exc:
            future.cancel()
            raise TranslationError("Translation timed out") from exc
