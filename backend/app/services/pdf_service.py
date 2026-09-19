"""PDF upload validation, text extraction, and per-participant translation."""

from __future__ import annotations

import logging
import os
import uuid

from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

from app.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

_ALLOWED_EXTENSION = ".pdf"
_ALLOWED_MIME_TYPES = {"application/pdf"}
_PDF_MAGIC_BYTES = b"%PDF-"
_MAX_EXTRACTED_CHARS = 20000  # keep translation calls bounded


class PdfValidationError(Exception):
    """Safe-to-display validation failure."""


class PdfService:
    def __init__(self, translation_service: TranslationService, upload_dir: str, max_size_bytes: int):
        self.translation_service = translation_service
        self.upload_dir = upload_dir
        self.max_size_bytes = max_size_bytes
        os.makedirs(self.upload_dir, exist_ok=True)

    def validate(self, filename: str, mime_type: str, data: bytes) -> None:
        if not filename or not filename.lower().endswith(_ALLOWED_EXTENSION):
            raise PdfValidationError("Only PDF files are supported.")
        if mime_type not in _ALLOWED_MIME_TYPES:
            raise PdfValidationError("Only PDF files are supported.")
        if not data:
            raise PdfValidationError("The uploaded file is empty.")
        if len(data) > self.max_size_bytes:
            max_mb = self.max_size_bytes // (1024 * 1024)
            raise PdfValidationError(f"PDF files must be smaller than {max_mb} MB.")
        if not data.startswith(_PDF_MAGIC_BYTES):
            raise PdfValidationError("This file does not look like a valid PDF.")

    def save_temp(self, data: bytes) -> str:
        """Write to a server-generated filename - never trust the client's name."""
        safe_name = f"{uuid.uuid4().hex}.pdf"
        path = os.path.join(self.upload_dir, safe_name)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def extract_text(self, path: str) -> str:
        try:
            reader = PdfReader(path)
            if reader.is_encrypted:
                raise PdfValidationError("This PDF is password-protected and cannot be read.")
            pages_text = []
            for page in reader.pages:
                pages_text.append(page.extract_text() or "")
            text = "\n".join(pages_text).strip()
        except PdfReadError as exc:
            logger.warning("Corrupt PDF rejected: %s", exc)
            raise PdfValidationError("This PDF could not be read - it may be corrupted.") from exc
        finally:
            self.delete_temp(path)

        return text[:_MAX_EXTRACTED_CHARS]

    def delete_temp(self, path: str) -> None:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError as exc:
            logger.warning("Failed to delete temp PDF %s: %s", path, exc)

    def translate_for_members(self, text: str, members: list[dict]) -> dict[str, dict]:
        """Returns member id -> {text, targetLanguage, ok}."""
        if not text:
            return {
                member["id"]: {"text": "", "targetLanguage": member["language"], "ok": True}
                for member in members
            }

        source_language = self.translation_service.detect_language(text, default="en")
        results = self.translation_service.translate_for_members(text, source_language, members)
        return {
            member_id: {
                "text": result.text,
                "targetLanguage": result.target_language,
                "ok": result.ok,
            }
            for member_id, result in results.items()
        }
