import base64

import pytest

from app.services.translation_service import TranslationResult
from tests.pdf_fixtures import build_blank_pdf_bytes, build_pdf_bytes


class _StubTranslationService:
    """Deterministic stand-in: prefixes text with the target language code."""

    def detect_language(self, text, default="en"):
        return default

    def translate(self, text, target_language, source_language):
        if source_language == target_language:
            return TranslationResult(text=text, source_language=source_language, target_language=target_language, ok=True)
        return TranslationResult(text=f"[{target_language}] {text}", source_language=source_language, target_language=target_language, ok=True)

    def translate_for_members(self, text, source_language, members):
        return {m["id"]: self.translate(text, m["language"], source_language) for m in members}


@pytest.fixture(autouse=True)
def stub_translation(app):
    # Socket handlers close over the service instances captured at
    # registration time in create_app(), so swapping the app.extensions
    # entry after the fact would not reach them. Patch the bound methods on
    # the *existing* instance instead - handlers hold a reference to this
    # same object.
    stub = _StubTranslationService()
    real_service = app.extensions["translation_service"]
    real_service.detect_language = stub.detect_language
    real_service.translate = stub.translate
    real_service.translate_for_members = stub.translate_for_members
    yield


def _connect(socketio_ext, app):
    return socketio_ext.test_client(app)


def test_create_room_returns_room_joined_with_four_char_code(app, socketio_client):
    socketio_client.emit("create_room", {"name": "Seyram", "language": "en"})
    received = socketio_client.get_received()

    assert len(received) == 1
    assert received[0]["name"] == "room_joined"
    payload = received[0]["args"][0]
    assert len(payload["roomCode"]) == 4
    assert payload["you"]["name"] == "Seyram"
    assert payload["participants"] == [{"id": payload["you"]["id"], "name": "Seyram", "language": "en"}]


def test_create_room_rejects_invalid_language(app, socketio_client):
    socketio_client.emit("create_room", {"name": "Seyram", "language": "xx"})
    received = socketio_client.get_received()

    assert received[0]["name"] == "error"
    assert received[0]["args"][0]["code"] == "invalid_input"


def test_join_room_success_and_notifies_existing_member(app):
    from app.extensions import socketio as sio

    creator = sio.test_client(app)
    creator.emit("create_room", {"name": "Seyram", "language": "en"})
    room_code = creator.get_received()[0]["args"][0]["roomCode"]

    joiner = sio.test_client(app)
    joiner.emit("join_room", {"name": "Daniel", "language": "de", "roomCode": room_code})

    joiner_received = joiner.get_received()
    assert joiner_received[0]["name"] == "room_joined"
    assert len(joiner_received[0]["args"][0]["participants"]) == 2

    creator_received = creator.get_received()
    assert creator_received[0]["name"] == "user_joined"
    assert creator_received[0]["args"][0]["participant"]["name"] == "Daniel"
    # Seyram's language is "en", same as the system message template's source
    # language, so the stub returns it unchanged (no [xx] prefix).
    assert creator_received[0]["args"][0]["message"] == "Daniel joined the room"


def test_join_room_rejects_unknown_code(app, socketio_client):
    socketio_client.emit("join_room", {"name": "Daniel", "language": "de", "roomCode": "ZZZZ"})
    received = socketio_client.get_received()

    assert received[0]["name"] == "error"
    assert received[0]["args"][0]["code"] == "room_not_found"


def test_join_room_rejects_invalid_room_code_format(app, socketio_client):
    socketio_client.emit("join_room", {"name": "Daniel", "language": "de", "roomCode": "toolong"})
    received = socketio_client.get_received()

    assert received[0]["name"] == "error"
    assert received[0]["args"][0]["code"] == "invalid_input"


def test_send_message_delivers_per_recipient_translation(app):
    from app.extensions import socketio as sio

    seyram = sio.test_client(app)
    seyram.emit("create_room", {"name": "Seyram", "language": "en"})
    room_code = seyram.get_received()[0]["args"][0]["roomCode"]

    daniel = sio.test_client(app)
    daniel.emit("join_room", {"name": "Daniel", "language": "de", "roomCode": room_code})
    daniel.get_received()  # drain room_joined
    seyram.get_received()  # drain user_joined

    seyram.emit("send_message", {"text": "Hello Daniel, how is your day going?"})

    seyram_received = seyram.get_received()
    daniel_received = daniel.get_received()

    seyram_msg = next(m for m in seyram_received if m["name"] == "message_received")["args"][0]
    daniel_msg = next(m for m in daniel_received if m["name"] == "message_received")["args"][0]

    assert seyram_msg["isOwn"] is True
    assert seyram_msg["translatedText"] == "Hello Daniel, how is your day going?"
    assert daniel_msg["isOwn"] is False
    assert daniel_msg["translatedText"] == "[de] Hello Daniel, how is your day going?"
    assert daniel_msg["senderName"] == "Seyram"


def test_send_message_rejects_empty_text(app, socketio_client):
    socketio_client.emit("create_room", {"name": "Seyram", "language": "en"})
    socketio_client.get_received()

    socketio_client.emit("send_message", {"text": "   "})
    received = socketio_client.get_received()

    assert received[0]["name"] == "error"
    assert received[0]["args"][0]["code"] == "invalid_input"


def test_send_message_without_room_returns_error(app, socketio_client):
    socketio_client.emit("send_message", {"text": "hello"})
    received = socketio_client.get_received()

    assert received[0]["name"] == "error"
    assert received[0]["args"][0]["code"] == "not_in_room"


def test_leave_room_notifies_remaining_participants(app):
    from app.extensions import socketio as sio

    seyram = sio.test_client(app)
    seyram.emit("create_room", {"name": "Seyram", "language": "en"})
    room_code = seyram.get_received()[0]["args"][0]["roomCode"]

    daniel = sio.test_client(app)
    daniel.emit("join_room", {"name": "Daniel", "language": "de", "roomCode": room_code})
    daniel.get_received()
    seyram.get_received()

    daniel.emit("leave_room", {})
    seyram_received = seyram.get_received()

    left_event = next(m for m in seyram_received if m["name"] == "user_left")["args"][0]
    assert left_event["participant"]["name"] == "Daniel"
    assert [p["name"] for p in left_event["participants"]] == ["Seyram"]


def test_room_is_deleted_when_last_participant_disconnects(app):
    from app.extensions import socketio as sio

    room_service = app.extensions["room_service"]
    client = sio.test_client(app)
    client.emit("create_room", {"name": "Seyram", "language": "en"})
    room_code = client.get_received()[0]["args"][0]["roomCode"]

    assert room_service.room_exists(room_code) is True

    client.disconnect()

    assert room_service.room_exists(room_code) is False


def test_two_rooms_do_not_leak_messages_to_each_other(app):
    from app.extensions import socketio as sio

    room_a_creator = sio.test_client(app)
    room_a_creator.emit("create_room", {"name": "A1", "language": "en"})
    code_a = room_a_creator.get_received()[0]["args"][0]["roomCode"]

    room_b_creator = sio.test_client(app)
    room_b_creator.emit("create_room", {"name": "B1", "language": "en"})
    room_b_creator.get_received()

    room_a_creator.emit("send_message", {"text": "secret to room A"})
    room_a_creator.get_received()

    assert room_b_creator.get_received() == []


def test_upload_pdf_delivers_translated_text_to_each_participant(app):
    from app.extensions import socketio as sio

    seyram = sio.test_client(app)
    seyram.emit("create_room", {"name": "Seyram", "language": "en"})
    room_code = seyram.get_received()[0]["args"][0]["roomCode"]

    daniel = sio.test_client(app)
    daniel.emit("join_room", {"name": "Daniel", "language": "de", "roomCode": room_code})
    daniel.get_received()
    seyram.get_received()

    pdf_bytes = build_pdf_bytes("Hello World")
    seyram.emit(
        "upload_pdf",
        {
            "filename": "doc.pdf",
            "mimeType": "application/pdf",
            "data": base64.b64encode(pdf_bytes).decode("ascii"),
        },
    )

    seyram_received = seyram.get_received()
    daniel_received = daniel.get_received()

    shared_events = [m for m in seyram_received if m["name"] == "pdf_shared"]
    assert shared_events[0]["args"][0]["uploadedBy"] == "Seyram"

    seyram_result = next(m for m in seyram_received if m["name"] == "pdf_translation_complete")["args"][0]
    daniel_result = next(m for m in daniel_received if m["name"] == "pdf_translation_complete")["args"][0]

    assert seyram_result["hasExtractableText"] is True
    assert "Hello World" in seyram_result["text"]
    assert daniel_result["targetLanguage"] == "de"
    assert daniel_result["text"] == "[de] Hello World"


def test_upload_pdf_with_no_extractable_text_reports_gracefully(app, socketio_client):
    socketio_client.emit("create_room", {"name": "Seyram", "language": "en"})
    socketio_client.get_received()

    pdf_bytes = build_blank_pdf_bytes()
    socketio_client.emit(
        "upload_pdf",
        {
            "filename": "scanned.pdf",
            "mimeType": "application/pdf",
            "data": base64.b64encode(pdf_bytes).decode("ascii"),
        },
    )

    received = socketio_client.get_received()
    result = next(m for m in received if m["name"] == "pdf_translation_complete")["args"][0]

    assert result["hasExtractableText"] is False
    assert "OCR" in result["message"]


def test_upload_pdf_rejects_oversized_file(app, socketio_client):
    socketio_client.emit("create_room", {"name": "Seyram", "language": "en"})
    socketio_client.get_received()

    app.extensions["pdf_service"].max_size_bytes = 10

    pdf_bytes = build_pdf_bytes("Hello World")
    socketio_client.emit(
        "upload_pdf",
        {
            "filename": "doc.pdf",
            "mimeType": "application/pdf",
            "data": base64.b64encode(pdf_bytes).decode("ascii"),
        },
    )

    received = socketio_client.get_received()
    assert received[0]["name"] == "error"
    assert received[0]["args"][0]["code"] == "invalid_pdf"


def test_upload_pdf_rejects_non_pdf_file(app, socketio_client):
    socketio_client.emit("create_room", {"name": "Seyram", "language": "en"})
    socketio_client.get_received()

    socketio_client.emit(
        "upload_pdf",
        {
            "filename": "doc.txt",
            "mimeType": "text/plain",
            "data": base64.b64encode(b"just text").decode("ascii"),
        },
    )

    received = socketio_client.get_received()
    assert received[0]["name"] == "error"
    assert received[0]["args"][0]["code"] == "invalid_pdf"
