import re

from app.utils.languages import is_supported_language

_ROOM_CODE_RE = re.compile(r"^[A-Z0-9]{4}$")

# Strip control characters (except newline/tab) that serve no display purpose
# and could be used to smuggle terminal/log injection payloads.
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class ValidationError(Exception):
    """Raised when client-supplied data fails validation. Message is safe to show the user."""


def sanitize_text(value: str) -> str:
    """Trim and strip control characters. XSS protection relies on the React
    frontend rendering this as text content (never innerHTML), which escapes
    HTML by default — escaping it again here would corrupt legitimate text
    like "AT&T" into "AT&amp;T" on screen.
    """
    return _CONTROL_CHARS_RE.sub("", value.strip())


def validate_name(name: object, max_length: int) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("Please enter your name.")
    cleaned = name.strip()
    if len(cleaned) > max_length:
        raise ValidationError(f"Name must be {max_length} characters or fewer.")
    return sanitize_text(cleaned)


def validate_room_code(code: object) -> str:
    if not isinstance(code, str):
        raise ValidationError("Invalid room code.")
    cleaned = code.strip().upper()
    if not _ROOM_CODE_RE.match(cleaned):
        raise ValidationError("Room codes are 4 letters or numbers.")
    return cleaned


def validate_language(code: object) -> str:
    if not isinstance(code, str) or not is_supported_language(code):
        raise ValidationError("Please choose a supported language.")
    return code


def validate_message_text(text: object, max_length: int) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValidationError("Message cannot be empty.")
    cleaned = text.strip()
    if len(cleaned) > max_length:
        raise ValidationError(f"Messages must be {max_length} characters or fewer.")
    return sanitize_text(cleaned)
