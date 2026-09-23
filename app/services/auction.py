import random

from db import display_name_exists
from datetime import datetime, timedelta
from app.services.nocodb import resolve_attachment_urls

ANTI_SNIPE_WINDOW = timedelta(minutes=4)

NAME_ADJECTIVES = [
    "Quiet",
    "Brave",
    "Sunny",
    "Clever",
    "Gentle",
    "Swift",
    "Cozy",
    "Bright",
    "Calm",
    "Bold",
    "Merry",
    "Lucky",
    "Jolly",
    "Mighty",
    "Wandering",
    "Silent",
]
NAME_NOUNS = [
    "Otter",
    "Fern",
    "Panda",
    "Falcon",
    "Maple",
    "Comet",
    "Badger",
    "Willow",
    "Sparrow",
    "Lynx",
    "Cedar",
    "Heron",
    "Pebble",
    "Ember",
    "Fox",
    "Harbor",
]


def generate_display_name():
    for _ in range(20):
        candidate = f"{random.choice(NAME_ADJECTIVES)}{random.choice(NAME_NOUNS)}{random.randint(10, 99)}"
        if not display_name_exists(candidate):
            return candidate
    raise RuntimeError("Could not generate a unique display name")


def parse_shipping_countries(shipping_countries):
    return [c.strip().lower() for c in (shipping_countries or "").split(",") if c.strip()]


def country_can_bid(allowed_countries, bidder_country):
    if not allowed_countries:
        return True
    if not bidder_country:
        return None
    return bidder_country.strip().lower() in allowed_countries


def transform_auction_item(item, bidder_country=None):
    """Reshape a raw NocoDB Auction Items row for public display."""
    allowed = parse_shipping_countries(item.get("Shipping Countries"))
    can_bid = country_can_bid(allowed, bidder_country)

    return {
        "id": item.get("Id"),
        "item_name": item.get("Item Name"),
        "description": item.get("Description"),
        "category": item.get("Category"),
        "donator_name": item.get("Donator Name"),
        "photos": resolve_attachment_urls(item.get("Photos")),
        "starting_bid": item.get("Starting Bid"),
        "current_bid": item.get("Current Bid"),
        "highest_bidder": item.get("Current Bidder Name"),
        "auction_end_time": item.get("Auction End Time"),
        "shipping_from": item.get("Location"),
        "shipping_type": item.get("Shipping Type"),
        "estimated_shipping_cost": item.get("Estimated Shipping Cost"),
        "can_bid": can_bid,
    }


def place_bid(bidder, item_id, amount):
    """Validate and record a bid. If this bid lands within the
    anti-snipe window, push the end time out so bidding stays open for 4 mins.
    Returns (payload_dict, status_code)."""
    from app.services.nocodb import nocodb_get, nocodb_patch, nocodb_post

    item_resp = nocodb_get("Auction Items", item_id)
    if item_resp.status_code != 200:
        return {"error": "Auction item not found"}, 404
    item = item_resp.json()

    now = datetime.utcnow()
    end_time = None
    end_time_raw = item.get("Auction End Time")
    if end_time_raw:
        end_time = datetime.fromisoformat(end_time_raw.replace("Z", "+00:00")).replace(tzinfo=None)
        if now >= end_time:
            return {"error": "This auction has ended"}, 400

    allowed = parse_shipping_countries(item.get("Shipping Countries"))
    if allowed and bidder.country.strip().lower() not in allowed:
        return {"error": "This item cannot ship to your country"}, 403

    current_bid = float(item.get("Current Bid") or item.get("Starting Bid") or 0)
    if amount <= current_bid:
        return {"error": f"Bid must be higher than the current bid (${current_bid:.2f})"}, 400

    bid_response = nocodb_post(
        "Bids",
        {
            "Item Id": item_id,
            "Bidder Display Name": bidder.display_name,
            "Bidder Id": bidder.id,
            "Amount": amount,
        },
    )
    if bid_response.status_code not in (200, 201):
        return bid_response.json(), bid_response.status_code

    update_fields = {
        "Id": item_id,
        "Current Bid": amount,
        "Current Bidder Name": bidder.display_name,
        "Current Bidder Id": bidder.id,
    }

    extended = False
    if end_time and (end_time - now) < ANTI_SNIPE_WINDOW:
        new_end_time = now + ANTI_SNIPE_WINDOW
        update_fields["Auction End Time"] = new_end_time.isoformat() + "Z"
        extended = True

    nocodb_patch("Auction Items", update_fields)

    return {"message": "Bid placed", "amount": amount, "extended": extended}, 201


def top_bidders(items, limit=8):
    """Rank bidders by how much they're currently winning, added up
    across every item where they're the current top bid. Returns a
    list sorted highest-total first."""
    totals = {}
    for item in items:
        bidder_id = item.get("Current Bidder Id")
        current_bid = item.get("Current Bid")
        if not bidder_id or not current_bid:
            continue
        if bidder_id not in totals:
            totals[bidder_id] = {
                "bidder_id": bidder_id,
                "display_name": item.get("Current Bidder Name"),
                "total": 0,
                "items_winning": 0,
            }
        totals[bidder_id]["total"] += float(current_bid)
        totals[bidder_id]["items_winning"] += 1

    ranked = sorted(totals.values(), key=lambda b: b["total"], reverse=True)
    return ranked[:limit]


def broadcast_bid_update(item_id):
    """Push the new price and leaderboard out to every connected
    browser, right after a bid is saved. Re-reads from NocoDB rather
    than trying to track it in memory, so everyone sees exactly what
    the database has."""
    from app.extensions import socketio
    from app.services.nocodb import nocodb_get, nocodb_list

    item_resp = nocodb_get("Auction Items", item_id)
    if item_resp.status_code == 200:
        socketio.emit("item_updated", transform_auction_item(item_resp.json()))

    items = nocodb_list("Auction Items", limit=1000)
    socketio.emit("leaderboard_updated", top_bidders(items))
