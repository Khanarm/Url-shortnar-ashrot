from flask import Blueprint, redirect, render_template, session
from database import urls, users
from config import Config
from datetime import datetime
from bson import ObjectId


links_bp = Blueprint("links", __name__)


# =========================================================
# SHORT LINK
# =========================================================

@links_bp.route("/<short_code>")
@links_bp.route("/<short_code>/<alias>")
def redirect_url(short_code, alias=None):

    url = urls.find_one({
        "short_code": short_code
    })

    if not url:
        return "Link not found", 404

    return redirect(f"/go/{short_code}")


# =========================================================
# PAGE 1
# =========================================================

@links_bp.route("/go/<short_code>")
def go(short_code):

    url = urls.find_one({
        "short_code": short_code
    })

    if not url:
        return "Link not found", 404

    # Start a NEW verification session for this link.
    session.pop(f"verified_{short_code}", None)
    session[f"page1_{short_code}"] = True

    return render_template(
        "wait.html",
        short_code=short_code
    )


# =========================================================
# PAGE 2
# =========================================================

@links_bp.route("/wait1/<short_code>")
def wait1(short_code):

    url = urls.find_one({
        "short_code": short_code
    })

    if not url:
        return "Link not found", 404

    # User must come through Page 1.
    if not session.get(f"page1_{short_code}"):
        return redirect(f"/go/{short_code}")

    # Page 1 completed.
    session[f"page2_{short_code}"] = True

    return render_template(
        "wait1.html",
        short_code=short_code
    )


# =========================================================
# FINAL DESTINATION
# =========================================================

@links_bp.route("/complete/<short_code>")
def complete(short_code):

    url = urls.find_one({
        "short_code": short_code
    })

    if not url:
        return "Link not found", 404

    # Both verification pages must have been visited.
    if not session.get(f"page1_{short_code}"):
        return redirect(f"/go/{short_code}")

    if not session.get(f"page2_{short_code}"):
        return redirect(f"/wait1/{short_code}")

    # Mark verification complete.
    session[f"verified_{short_code}"] = True

    # Original destination saved by API.
    original_url = str(
        url.get("original_url", "")
    ).strip()

    if not original_url:
        return "Original URL not found", 404

    # Count click only after successful verification.
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


# =========================================================
# OLD WAIT ROUTE
# =========================================================

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
