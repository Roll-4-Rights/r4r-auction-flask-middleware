from flask import Blueprint, request

from app.services.errors import handle_route_errors
from app.services.nocodb import as_flask_response, nocodb_get

bp = Blueprint("donator_profiles", __name__)


@bp.route("/api/donator-profiles", methods=["GET"])
@handle_route_errors("Failed to load donator profiles")
def get_donator_profiles():
    """Public directory of donator profiles, backed by the NocoDB
    "Donator Profiles" table (Social Media Name, Wares Description,
    Location, Website).

    Query params (`limit`, `offset`, etc.) are forwarded straight to
    NocoDB, and — unlike `list_records_response` — the response here
    keeps NocoDB's `pageInfo` block (totalRows, isLastPage, ...) so
    the frontend can drive Next/Previous controls.

    Example: GET /api/donator-profiles?limit=9&offset=9  (page 2 of a
    3x3 grid)
    """
    return as_flask_response(nocodb_get("Donator Profiles", **request.args))