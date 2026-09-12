from flask import (
    Blueprint,
    redirect,
    render_template
)

from database import (
    urls,
    users
)

from config import Config

from datetime import datetime


links_bp = Blueprint(
    "links",
    __name__
)


@links_bp.route("/<short_code>")
@links_bp.route("/<short_code>/<alias>")
def redirect_url(
    short_code,
    alias=None
):

    url = urls.find_one({
        "short_code": short_code
    })

    if not url:

        return "Link not found", 404

    return redirect(
        f"/wait/{short_code}"
    )


@links_bp.route(
    "/wait/<short_code>"
)
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


@links_bp.route(
    "/wait1/<short_code>"
)
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


@links_bp.route(
    "/go/<short_code>"
)
def go(short_code):

    url = urls.find_one({
        "short_code": short_code
    })

    if not url:

        return "Link not found", 404

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

    # ---------------------------------
    # Earning only for API/user links
    # ---------------------------------

    owner_id = url.get(
        "owner_id"
    )

    if owner_id:

        today = datetime.utcnow().strftime(
            "%Y-%m-%d"
        )

        earning = Config.EARNING_PER_VISIT_USDT

        users.update_one(
            {
                "_id": __import__(
                    "bson"
                ).ObjectId(owner_id)
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

    return redirect(
        url["original_url"]
    )
