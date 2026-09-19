import pytest

import app.services.translation_service as translation_module
from app.services.translation_service import TranslationService


class _FakeGoogleTranslator:
    """Stand-in for deep_translator.GoogleTranslator with scripted behavior."""

    fail = False
    raise_exception = None

    def __init__(self, source, target):
        self.source = source
        self.target = target
        self._source = "en" if source == "auto" else source

    def translate(self, text):
        if _FakeGoogleTranslator.raise_exception:
            raise _FakeGoogleTranslator.raise_exception
        if _FakeGoogleTranslator.fail:
            raise RuntimeError("simulated Google failure")
        return f"[{self.target}] {text}"


class _FakeMyMemoryTranslator:
    fail = False

    def __init__(self, source, target):
        self.source = source
        self.target = target

    def translate(self, text):
        if _FakeMyMemoryTranslator.fail:
            raise RuntimeError("simulated MyMemory failure")
        return f"(mm:{self.target}) {text}"


@pytest.fixture(autouse=True)
def reset_fakes(monkeypatch):
    _FakeGoogleTranslator.fail = False
    _FakeGoogleTranslator.raise_exception = None
    _FakeMyMemoryTranslator.fail = False
    monkeypatch.setattr(translation_module, "GoogleTranslator", _FakeGoogleTranslator)
    monkeypatch.setattr(translation_module, "MyMemoryTranslator", _FakeMyMemoryTranslator)
    translation_module._cache.clear()
    translation_module._cache_order.clear()


@pytest.fixture()
def service():
    return TranslationService(timeout_seconds=2, max_retries=1)


def test_translate_returns_unchanged_text_when_source_equals_target(service):
    result = service.translate("Hello", "en", "en")
    assert result.ok is True
    assert result.text == "Hello"
    assert result.fallback_used is False


def test_translate_uses_google_by_default(service):
    result = service.translate("Hello", "fr", "en")
    assert result.ok is True
    assert result.text == "[fr] Hello"
    assert result.fallback_used is False


def test_translate_falls_back_to_mymemory_when_google_fails(service):
    _FakeGoogleTranslator.fail = True
    result = service.translate("Hello", "fr", "en")
    assert result.ok is True
    assert result.fallback_used is True
    assert result.text == "(mm:fr-FR) Hello"


def test_translate_returns_original_text_when_all_providers_fail(service):
    _FakeGoogleTranslator.fail = True
    _FakeMyMemoryTranslator.fail = True
    result = service.translate("Hello", "fr", "en")
    assert result.ok is False
    assert result.fallback_used is True
    assert result.text == "Hello"


def test_translate_caches_identical_requests(service):
    result1 = service.translate("Hello", "fr", "en")
    _FakeGoogleTranslator.fail = True  # would fail now if the cache were bypassed
    result2 = service.translate("Hello", "fr", "en")
    assert result1.text == result2.text == "[fr] Hello"


def test_translate_for_members_groups_by_target_language(service):
    members = [
        {"id": "a", "language": "en"},
        {"id": "b", "language": "fr"},
        {"id": "c", "language": "fr"},
    ]
    results = service.translate_for_members("Hi", "en", members)
    assert results["a"].text == "Hi"  # same as source language
    assert results["b"].text == results["c"].text == "[fr] Hi"


def test_translate_empty_text_is_a_noop(service):
    result = service.translate("   ", "fr", "en")
    assert result.ok is True
    assert result.text == "   "


def test_detect_language_falls_back_on_failure(service):
    _FakeGoogleTranslator.raise_exception = RuntimeError("boom")
    detected = service.detect_language("Bonjour", default="fr")
    assert detected == "fr"
