import os
import shutil

import pytest

from app.services.pdf_service import PdfService, PdfValidationError
from app.services.translation_service import TranslationService
from tests.pdf_fixtures import build_blank_pdf_bytes, build_pdf_bytes

UPLOAD_DIR = "tests/tmp_pdf_uploads"


@pytest.fixture()
def service():
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    svc = PdfService(
        translation_service=TranslationService(),
        upload_dir=UPLOAD_DIR,
        max_size_bytes=1024 * 1024,
    )
    yield svc
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)


def test_validate_accepts_valid_pdf(service):
    service.validate("doc.pdf", "application/pdf", build_pdf_bytes())  # should not raise


def test_validate_rejects_non_pdf_extension(service):
    with pytest.raises(PdfValidationError):
        service.validate("doc.exe", "application/pdf", build_pdf_bytes())


def test_validate_rejects_wrong_mime_type(service):
    with pytest.raises(PdfValidationError):
        service.validate("doc.pdf", "image/png", build_pdf_bytes())


def test_validate_rejects_empty_file(service):
    with pytest.raises(PdfValidationError):
        service.validate("doc.pdf", "application/pdf", b"")


def test_validate_rejects_oversized_file(service):
    service.max_size_bytes = 10
    with pytest.raises(PdfValidationError):
        service.validate("doc.pdf", "application/pdf", build_pdf_bytes())


def test_validate_rejects_file_without_pdf_magic_bytes(service):
    with pytest.raises(PdfValidationError):
        service.validate("doc.pdf", "application/pdf", b"not a real pdf at all")


def test_save_temp_uses_server_generated_filename_not_client_name(service):
    path = service.save_temp(build_pdf_bytes())
    try:
        assert os.path.exists(path)
        assert "../" not in path
        assert os.path.dirname(path) == UPLOAD_DIR
    finally:
        service.delete_temp(path)


def test_extract_text_returns_pdf_content_and_deletes_temp_file(service):
    path = service.save_temp(build_pdf_bytes("Hello World"))
    text = service.extract_text(path)
    assert "Hello World" in text
    assert not os.path.exists(path)  # cleaned up automatically


def test_extract_text_returns_empty_string_for_pdf_with_no_text(service):
    path = service.save_temp(build_blank_pdf_bytes())
    text = service.extract_text(path)
    assert text == ""


def test_extract_text_raises_for_corrupt_pdf(service):
    path = service.save_temp(b"%PDF-1.4\nthis is not a real pdf structure")
    with pytest.raises(PdfValidationError):
        service.extract_text(path)
    assert not os.path.exists(path)  # cleaned up even on failure
