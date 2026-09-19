import logging

from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import socketio
from app.services import PdfService, RoomService, TranslationService


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    logging.basicConfig(level=logging.INFO if not app.config["DEBUG"] else logging.DEBUG)

    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    translation_service = TranslationService(
        timeout_seconds=app.config["TRANSLATION_TIMEOUT_SECONDS"],
        max_retries=app.config["TRANSLATION_MAX_RETRIES"],
        deepl_api_key=app.config["DEEPL_API_KEY"],
    )
    room_service = RoomService(
        max_participants=app.config["MAX_PARTICIPANTS_PER_ROOM"],
        code_length=app.config["ROOM_CODE_LENGTH"],
    )
    pdf_service = PdfService(
        translation_service=translation_service,
        upload_dir=app.config["PDF_UPLOAD_DIR"],
        max_size_bytes=app.config["MAX_PDF_SIZE_BYTES"],
    )

    app.extensions["translation_service"] = translation_service
    app.extensions["room_service"] = room_service
    app.extensions["pdf_service"] = pdf_service

    socketio.init_app(
        app,
        cors_allowed_origins=app.config["CORS_ORIGINS"],
        async_mode="eventlet",
        max_http_buffer_size=app.config["MAX_PDF_SIZE_BYTES"] * 2,
    )

    from app.routes.api import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    from app.sockets import handlers  # noqa: F401 - registers event handlers as a side effect

    handlers.init_socket_handlers(socketio, room_service, translation_service, pdf_service, app.config)

    return app
