import secrets
import string

_ALPHABET = string.ascii_uppercase + string.digits
_AMBIGUOUS = {"0", "O", "1", "I"}
_SAFE_ALPHABET = "".join(c for c in _ALPHABET if c not in _AMBIGUOUS)


def generate_room_code(length: int = 4) -> str:
    return "".join(secrets.choice(_SAFE_ALPHABET) for _ in range(length))
