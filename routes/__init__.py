from flask import Blueprint, redirect, request, url_for
from database import db
from models import URL

links_bp = Blueprint("links", __name__)


@links_bp.route("/<short_code>")
def redirect_url(short_code):

    url = URL.query.filter_by(short_code=short_code).first()

    if not url:
        return "Link not found", 404

    url.clicks += 1
    db.session.commit()

    return redirect(url.original_url)


@links_bp.route("/delete/<int:url_id>", methods=["POST"])
def delete_link(url_id):

    url = URL.query.get_or_404(url_id)

    db.session.delete(url)
    db.session.commit()

    return redirect(url_for("dashboard.dashboard"))
