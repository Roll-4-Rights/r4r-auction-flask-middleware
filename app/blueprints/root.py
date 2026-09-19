from flask import Blueprint, jsonify

bp = Blueprint("root", __name__)


@bp.route("/")
def index():
    return jsonify(
        {
            "service": "Roll4Rights Auction API",
            "status": "running",
        }
    ), 200


@bp.route("/favicon.ico")
def favicon():
    return "", 204
