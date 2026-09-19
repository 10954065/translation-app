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
    """Temporary diagnostic: calls each provider's raw client directly (no
    retry/timeout wrapper) and reports the real exception. Not wired into any
    client flow - safe to remove once the production translation failure is
    root-caused."""
    from deep_translator import DeeplTranslator, GoogleTranslator, MyMemoryTranslator

    result = {}
    deepl_key = current_app.config.get("DEEPL_API_KEY", "")
    result["deepl_key_configured"] = bool(deepl_key)

    if deepl_key:
        try:
            translated = DeeplTranslator(source="en", target="fr", api_key=deepl_key).translate("hello")
            result["deepl"] = {"ok": True, "text": translated}
        except Exception as exc:  # noqa: BLE001 - diagnostic only
            result["deepl"] = {"ok": False, "error": repr(exc), "traceback": traceback.format_exc()}
    else:
        result["deepl"] = {"ok": False, "error": "no key configured"}

    try:
        translated = GoogleTranslator(source="en", target="fr").translate("hello")
        result["google"] = {"ok": True, "text": translated}
    except Exception as exc:  # noqa: BLE001 - diagnostic only
        result["google"] = {"ok": False, "error": repr(exc), "traceback": traceback.format_exc()}

    try:
        translated = MyMemoryTranslator(source="en-GB", target="fr-FR").translate("hello")
        result["mymemory"] = {"ok": True, "text": translated}
    except Exception as exc:  # noqa: BLE001 - diagnostic only
        result["mymemory"] = {"ok": False, "error": repr(exc), "traceback": traceback.format_exc()}

    return jsonify(result)
