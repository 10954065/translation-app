import eventlet

eventlet.monkey_patch()

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from app import create_app  # noqa: E402
from app.extensions import socketio  # noqa: E402

app = create_app()

if __name__ == "__main__":
    socketio.run(
        app,
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
    )
