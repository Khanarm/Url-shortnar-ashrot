from flask import Blueprint, redirect, render_template
from database import urls, users
from config import Config
from datetime import datetime
from bson import ObjectId


links_bp = Blueprint("links", __name__)


@links_bp.route("/<short_code>")
@links_bp.route("/<short_code>/<alias>")
def redirect_url(short_code, alias=None):

    url = urls.find_one({
        "short_code": short_code
    })

    if not url:
        return "Link not found", 404

    return redirect(f"/wait/{short_code}")


@links_bp.route("/wait/<short_code>")
def wait_page(short_code):

    url = urls.find_one({
        "short_code": short_code
    })

    if not url:
        return "Link not found", 404

    return render_template(
        "wait.html",
        short_code=short_code
    )


@links_bp.route("/wait1/<short_code>")
def wait1(short_code):

    url = urls.find_one({
        "short_code": short_code
    })

    if not url:
        return "Link not found", 404

    return render_template(
        "wait1.html",
        short_code=short_code
    )


@links_bp.route("/go/<short_code>")
def go(short_code):

    # Find the saved short-link record
    url = urls.find_one({
        "short_code": short_code
    })

    if not url:
        return "Link not found", 404

    # IMPORTANT:
    # Always use the original_url saved by the API.
    original_url = str(
        url.get("original_url", "")
    ).strip()

    if not original_url:
        return "Original URL not found", 404

    # Count click
    urls.update_one(
        {
            "_id": url["_id"]
        },
        {
            "$inc": {
                "clicks": 1
            }
        }
    )

    # Earning
    owner_id = url.get("owner_id")

    if owner_id:

        today = datetime.utcnow().strftime("%Y-%m-%d")

        earning = Config.EARNING_PER_VISIT_USDT

        try:
            users.update_one(
                {
                    "_id": ObjectId(str(owner_id))
                },
                {
                    "$inc": {
                        "today_earning": earning,
                        "total_earning": earning,
                        "available_balance": earning
                    },
                    "$set": {
                        "last_earning_date": today
                    }
                }
            )
        except Exception:
            pass

    # FINAL DESTINATION
    return redirect(original_url)
