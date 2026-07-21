from flask import Blueprint, redirect, url_for
from bson import ObjectId
from database import urls

links_bp = Blueprint("links", __name__)


@links_bp.route("/<short_code>")
def redirect_url(short_code):

    url = urls.find_one({"short_code": short_code})

    if not url:
        return "Link not found", 404

    urls.update_one(
        {"_id": url["_id"]},
        {"$inc": {"clicks": 1}}
    )

    return redirect(url["original_url"])


@links_bp.route("/delete/<url_id>", methods=["POST"])
def delete_link(url_id):

    urls.delete_one({"_id": ObjectId(url_id)})

    return redirect(url_for("dashboard.dashboard"))
