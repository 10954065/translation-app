import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app import create_app
from app.config import Config
from app.extensions import socketio as socketio_ext


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    PDF_UPLOAD_DIR = "tests/tmp_uploads"


@pytest.fixture()
def app():
    application = create_app(TestConfig)
    yield application


@pytest.fixture()
def socketio_client(app):
    return socketio_ext.test_client(app)
