from flask import Blueprint, render_template, redirect, url_for
from models import URL
from database import db

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/dashboard")
def dashboard():

    urls = URL.query.all()

    total_links = len(urls)

    total_clicks = sum(
        url.clicks for url in urls
    )

    return render_template(
        "dashboard.html",
        urls=urls,
        total_links=total_links,
        total_clicks=total_clicks
    )

@dashboard_bp.route("/delete/<int:id>")
def delete_url(id):

    url = URL.query.get_or_404(id)

    db.session.delete(url)
    db.session.commit()

    return redirect(url_for("dashboard.dashboard"))
