import pytest

from app.utils.validators import (
    ValidationError,
    validate_language,
    validate_message_text,
    validate_name,
    validate_room_code,
)


def test_validate_name_accepts_valid_name():
    assert validate_name("Seyram", 40) == "Seyram"


def test_validate_name_rejects_empty_name():
    with pytest.raises(ValidationError):
        validate_name("   ", 40)


def test_validate_name_rejects_non_string():
    with pytest.raises(ValidationError):
        validate_name(None, 40)


def test_validate_name_rejects_too_long():
    with pytest.raises(ValidationError):
        validate_name("x" * 41, 40)


def test_validate_name_strips_control_characters():
    assert validate_name("Dan\x00iel", 40) == "Daniel"


def test_validate_room_code_normalizes_case():
    assert validate_room_code("wdfb") == "WDFB"


@pytest.mark.parametrize("bad_code", ["", "ABC", "ABCDE", "AB CD", None, 123])
def test_validate_room_code_rejects_invalid(bad_code):
    with pytest.raises(ValidationError):
        validate_room_code(bad_code)


def test_validate_language_accepts_supported_code():
    assert validate_language("en") == "en"


def test_validate_language_rejects_unsupported_code():
    with pytest.raises(ValidationError):
        validate_language("xx")


def test_validate_message_text_rejects_empty():
    with pytest.raises(ValidationError):
        validate_message_text("   ", 2000)


def test_validate_message_text_rejects_too_long():
    with pytest.raises(ValidationError):
        validate_message_text("x" * 2001, 2000)


def test_validate_message_text_trims_whitespace():
    assert validate_message_text("  hello  ", 2000) == "hello"
