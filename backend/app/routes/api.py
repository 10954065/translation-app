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
