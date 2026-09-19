from flask import Blueprint, jsonify, request

from app.decorators import require_api_key
from app.services.errors import handle_route_errors
from app.services.nocodb import as_flask_response, extract_first_record, list_records_response, nocodb_get, nocodb_post

bp = Blueprint("content", __name__)




@bp.route("/api/site-content", methods=["GET"])
@handle_route_errors("Failed to load site content")
def get_site_content():
    response = nocodb_get("Site Content", **request.args)
    record = extract_first_record(response.json())
    return jsonify(record or {}), response.status_code





@bp.route("/api/banner-messages", methods=["GET"])
@handle_route_errors("Failed to load banner messages")
def get_banner_messages():
    return list_records_response(
        "Banner Messages",
        limit=1000,
        where="(Active,eq,1)",
        sort="-Message,-Sort Order",
    )

@bp.route("/api/banner-messages", methods=["POST"])
@require_api_key
@handle_route_errors("Failed to create banner message")
def create_banner_message():
    return as_flask_response(nocodb_post("Banner Messages", request.json))
