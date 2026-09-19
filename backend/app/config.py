import os


def _split_origins(raw: str) -> list[str]:
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    FLASK_ENV = os.environ.get("FLASK_ENV", "production")
    DEBUG = FLASK_ENV == "development"

    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

    CORS_ORIGINS = _split_origins(os.environ.get("CORS_ORIGINS", "http://localhost:5173"))

    TRANSLATION_PROVIDER = os.environ.get("TRANSLATION_PROVIDER", "google")
    TRANSLATION_TIMEOUT_SECONDS = float(os.environ.get("TRANSLATION_TIMEOUT_SECONDS", "6"))
    TRANSLATION_MAX_RETRIES = int(os.environ.get("TRANSLATION_MAX_RETRIES", "2"))

    MAX_PDF_SIZE_MB = int(os.environ.get("MAX_PDF_SIZE_MB", "10"))
    MAX_PDF_SIZE_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024
    PDF_UPLOAD_DIR = os.environ.get("PDF_UPLOAD_DIR", "uploads")

    DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() == "true"

    MAX_MESSAGE_LENGTH = 2000
    MAX_NAME_LENGTH = 40
    MAX_PARTICIPANTS_PER_ROOM = 30
    ROOM_CODE_LENGTH = 4
