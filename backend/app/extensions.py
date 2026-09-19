from flask_socketio import SocketIO

# Created once, bound to the app inside create_app(). Kept in its own module
# so route/socket handler modules can import it without circular imports.
socketio = SocketIO(cors_allowed_origins=[], async_mode="eventlet", logger=False, engineio_logger=False)
