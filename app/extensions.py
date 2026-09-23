from flask import jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_socketio import SocketIO

login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address, default_limits=[])
socketio = SocketIO()


def init_extensions(app):
    login_manager.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app, cors_allowed_origins=app.config["ALLOWED_ORIGINS"], async_mode="threading")

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": "Login required"}), 401