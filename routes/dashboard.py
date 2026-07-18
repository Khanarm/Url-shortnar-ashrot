from flask import Blueprint, render_template
from models import URL

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
