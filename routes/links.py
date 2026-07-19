from flask import Blueprint, redirect, render_template
from database import db
from models import URL

links_bp = Blueprint("links", __name__)


@links_bp.route("/<short_code>")
def redirect_url(short_code):

    url = URL.query.filter_by(short_code=short_code).first()

    if not url:
        return "Link not found", 404

    return redirect(f"/wait/{short_code}")


@links_bp.route("/wait/<short_code>")
def wait_page(short_code):

    url = URL.query.filter_by(short_code=short_code).first()

    if not url:
        return "Link not found", 404

    return render_template(
        "wait.html",
        short_code=short_code
    )


@links_bp.route("/go/<short_code>")
def go(short_code):

    url = URL.query.filter_by(short_code=short_code).first()

    if not url:
        return "Link not found", 404

    url.clicks += 1
    db.session.commit()

    return redirect(url.original_url)
