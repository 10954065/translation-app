"""Socket.IO event handlers.

Handlers stay thin: validate the payload, delegate to a service, emit a
response. Business logic (room lifecycle, translation) lives in app.services.

Event contract
--------------
Client -> Server:
  create_room  {name, language}
  join_room    {name, language, roomCode}
  leave_room   {}
  send_message {text}
  upload_pdf   {filename, mimeType, data(base64)}

Server -> Client:
  room_joined            {roomCode, you, participants, pdfDocument}
  user_joined            {participant, message, participants}   (per-recipient translated)
  user_left              {participant, message, participants}   (per-recipient translated)
  message_received       {id, roomId, senderId, senderName, originalText,
                           sourceLanguage, translatedText, targetLanguage,
                           timestamp, isOwn, translationOk}       (per-recipient translated)
  pdf_shared              {filename, uploadedBy}
  pdf_translation_complete {filename, text, targetLanguage, hasExtractableText, ok, message?}
  translation_error       {context, message}
  error                   {code, message}
"""

from __future__ import annotations

import base64
import binascii
import logging

from flask import request
from flask_socketio import join_room as sio_join_room
from flask_socketio import leave_room as sio_leave_room

from app.services.pdf_service import PdfValidationError
from app.services.room_service import RoomFullError, RoomNotFoundError, build_message
from app.utils.validators import (
    ValidationError,
    validate_language,
    validate_message_text,
    validate_name,
    validate_room_code,
)

logger = logging.getLogger(__name__)

_JOIN_TEMPLATE = "{name} joined the room"
_LEAVE_TEMPLATE = "{name} left the room"


def init_socket_handlers(socketio, room_service, translation_service, pdf_service, config):
    max_name_length = config["MAX_NAME_LENGTH"]
    max_message_length = config["MAX_MESSAGE_LENGTH"]

    def _room_state_payload(room, you):
        return {
            "roomCode": room.code,
            "you": you.to_public_dict(),
            "participants": room.participant_list(),
            "pdfDocument": room.pdf_document,
        }

    def _broadcast_system_message(room, exclude_sid, event_key, participant):
        recipients = [p for sid, p in room.participants.items() if sid != exclude_sid]
        if not recipients:
            return
        template = _JOIN_TEMPLATE if event_key == "user_joined" else _LEAVE_TEMPLATE
        text = template.format(name=participant.name)
        members = [{"id": p.sid, "language": p.language} for p in recipients]
        results = translation_service.translate_for_members(text, "en", members)
        participants_payload = room.participant_list()
        for p in recipients:
            result = results[p.sid]
            socketio.emit(
                event_key,
                {
                    "participant": participant.to_public_dict(),
                    "message": result.text,
                    "participants": participants_payload,
                },
                to=p.sid,
            )

    def _handle_leave(sid):
        room = room_service.find_room_for_sid(sid)
        if room is None:
            return
        room_code = room.code
        remaining_room, participant = room_service.remove_participant(room_code, sid)
        if participant is None:
            return
        sio_leave_room(room_code, sid=sid)
        if remaining_room is not None:
            _broadcast_system_message(remaining_room, exclude_sid=None, event_key="user_left", participant=participant)
        else:
            logger.info("Room %s fully cleaned up (all temporary data cleared)", room_code)

    @socketio.on("connect")
    def handle_connect():
        logger.info("Client connected: %s", request.sid)

    @socketio.on("disconnect")
    def handle_disconnect():
        logger.info("Client disconnected: %s", request.sid)
        _handle_leave(request.sid)

    @socketio.on("create_room")
    def handle_create_room(data):
        data = data or {}
        try:
            name = validate_name(data.get("name"), max_name_length)
            language = validate_language(data.get("language"))
        except ValidationError as exc:
            socketio.emit("error", {"code": "invalid_input", "message": str(exc)}, to=request.sid)
            return

        room = room_service.create_room()
        room, participant = room_service.add_participant(room.code, request.sid, name, language)
        sio_join_room(room.code)
        socketio.emit("room_joined", _room_state_payload(room, participant), to=request.sid)

    @socketio.on("join_room")
    def handle_join_room(data):
        data = data or {}
        try:
            room_code = validate_room_code(data.get("roomCode"))
            name = validate_name(data.get("name"), max_name_length)
            language = validate_language(data.get("language"))
        except ValidationError as exc:
            socketio.emit("error", {"code": "invalid_input", "message": str(exc)}, to=request.sid)
            return

        try:
            room, participant = room_service.add_participant(room_code, request.sid, name, language)
        except RoomNotFoundError as exc:
            socketio.emit("error", {"code": "room_not_found", "message": str(exc)}, to=request.sid)
            return
        except RoomFullError as exc:
            socketio.emit("error", {"code": "room_full", "message": str(exc)}, to=request.sid)
            return

        sio_join_room(room_code)
        socketio.emit("room_joined", _room_state_payload(room, participant), to=request.sid)
        _broadcast_system_message(room, exclude_sid=request.sid, event_key="user_joined", participant=participant)

    @socketio.on("leave_room")
    def handle_leave_room_event(_data):
        _handle_leave(request.sid)

    @socketio.on("send_message")
    def handle_send_message(data):
        data = data or {}
        room = room_service.find_room_for_sid(request.sid)
        if room is None:
            socketio.emit("error", {"code": "not_in_room", "message": "You are not in a room."}, to=request.sid)
            return
        sender = room.participants.get(request.sid)

        try:
            text = validate_message_text(data.get("text"), max_message_length)
        except ValidationError as exc:
            socketio.emit("error", {"code": "invalid_input", "message": str(exc)}, to=request.sid)
            return

        source_language = translation_service.detect_language(text, default=sender.language)
        message = build_message(sender, text, source_language)
        room_service.record_message(room.code)

        members = [p.to_public_dict() for p in room.participants.values()]
        results = translation_service.translate_for_members(text, source_language, members)

        any_failed = False
        for member_id, result in results.items():
            if not result.ok:
                any_failed = True
            socketio.emit(
                "message_received",
                {
                    "id": message.id,
                    "roomId": room.code,
                    "senderId": sender.sid,
                    "senderName": sender.name,
                    "originalText": text,
                    "sourceLanguage": source_language,
                    "translatedText": result.text,
                    "targetLanguage": result.target_language,
                    "timestamp": message.timestamp,
                    "isOwn": member_id == sender.sid,
                    "translationOk": result.ok,
                },
                to=member_id,
            )

        if any_failed:
            socketio.emit(
                "translation_error",
                {
                    "context": "message",
                    "message": "Translation temporarily unavailable for some participants. Original text was shown instead.",
                },
                to=sender.sid,
            )

    @socketio.on("upload_pdf")
    def handle_upload_pdf(data):
        data = data or {}
        room = room_service.find_room_for_sid(request.sid)
        if room is None:
            socketio.emit("error", {"code": "not_in_room", "message": "You are not in a room."}, to=request.sid)
            return
        sender = room.participants.get(request.sid)

        filename = data.get("filename") or ""
        mime_type = data.get("mimeType") or ""
        raw_b64 = data.get("data") or ""

        try:
            raw_bytes = base64.b64decode(raw_b64, validate=True)
        except (binascii.Error, ValueError):
            socketio.emit("error", {"code": "invalid_pdf", "message": "Could not read the uploaded file."}, to=request.sid)
            return

        try:
            pdf_service.validate(filename, mime_type, raw_bytes)
        except PdfValidationError as exc:
            socketio.emit("error", {"code": "invalid_pdf", "message": str(exc)}, to=request.sid)
            return

        socketio.emit("pdf_shared", {"filename": filename, "uploadedBy": sender.name}, to=room.code)

        path = pdf_service.save_temp(raw_bytes)
        try:
            text = pdf_service.extract_text(path)
        except PdfValidationError as exc:
            socketio.emit("error", {"code": "invalid_pdf", "message": str(exc)}, to=request.sid)
            return

        if not text:
            socketio.emit(
                "pdf_translation_complete",
                {
                    "filename": filename,
                    "text": "",
                    "hasExtractableText": False,
                    "ok": True,
                    "message": "This PDF does not contain extractable text. OCR is required for scanned/image-only documents.",
                },
                to=room.code,
            )
            return

        members = room.participant_list()
        translations = pdf_service.translate_for_members(text, members)
        any_failed = any(not r["ok"] for r in translations.values())

        for member_id, result in translations.items():
            socketio.emit(
                "pdf_translation_complete",
                {
                    "filename": filename,
                    "text": result["text"],
                    "targetLanguage": result["targetLanguage"],
                    "hasExtractableText": True,
                    "ok": result["ok"],
                },
                to=member_id,
            )

        if any_failed:
            socketio.emit(
                "translation_error",
                {
                    "context": "pdf",
                    "message": "Translation temporarily unavailable for some participants. Original text was shown instead.",
                },
                to=sender.sid,
            )

        room_service.set_pdf_document(room.code, {"filename": filename, "sharedBy": sender.name})
