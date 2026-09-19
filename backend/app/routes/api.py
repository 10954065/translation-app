import traceback

from flask import Blueprint, current_app, jsonify

from app.utils.languages import SUPPORTED_LANGUAGES

api_bp = Blueprint("api", __name__)


@api_bp.get("/health")
def health():
    room_service = current_app.extensions["room_service"]
    return jsonify({"status": "ok", "activeRooms": room_service.room_count()})


@api_bp.get("/languages")
def languages():
    return jsonify({"languages": SUPPORTED_LANGUAGES})


@api_bp.get("/rooms/<string:code>/exists")
def room_exists(code: str):
    room_service = current_app.extensions["room_service"]
    exists = room_service.room_exists(code.strip().upper())
    return jsonify({"exists": exists})


@api_bp.get("/debug/translation-check")
def translation_check():
    """Temporary diagnostic: calls each provider directly and reports the raw
    exception. Not wired into any client flow - safe to remove once the
    production translation failure is root-caused."""
    translation_service = current_app.extensions["translation_service"]
    result = {}

    try:
        text = translation_service._translate_with_google("hello", "en", "fr")
        result["google"] = {"ok": text is not None, "text": text}
    except Exception as exc:  # noqa: BLE001 - diagnostic only
        result["google"] = {"ok": False, "error": repr(exc), "traceback": traceback.format_exc()}

    try:
        text = translation_service._translate_with_mymemory("hello", "en", "fr")
        result["mymemory"] = {"ok": text is not None, "text": text}
    except Exception as exc:  # noqa: BLE001 - diagnostic only
        result["mymemory"] = {"ok": False, "error": repr(exc), "traceback": traceback.format_exc()}

    return jsonify(result)
