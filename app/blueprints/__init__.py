from app.blueprints.auction import bp as auction_bp
from app.blueprints.auth import bp as auth_bp
from app.blueprints.bidder import bp as bidder_bp
from app.blueprints.campaign import bp as campaign_bp
from app.blueprints.content import bp as content_bp
from app.blueprints.health import bp as health_bp
from app.blueprints.root import bp as root_bp
from app.blueprints.tables import bp as tables_bp
from app.blueprints.winner_claim import bp as winner_claim_bp
from app.blueprints.donator_profiles import bp as donator_profiles_bp

def register_blueprints(app):
    for blueprint in (
        health_bp,
        auth_bp,
        auction_bp,
        bidder_bp,
        winner_claim_bp,
        campaign_bp,
        content_bp,
        tables_bp,
        root_bp,
        donator_profiles_bp
    ):
        app.register_blueprint(blueprint)
