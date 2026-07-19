from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import or_, func
from models import URL
from database import db

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/dashboard")
def dashboard():

    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)

    query = URL.query

    if search:
        query = query.filter(
            or_(
                URL.original_url.ilike(f"%{search}%"),
                URL.short_code.ilike(f"%{search}%")
            )
        )

    query = query.order_by(URL.id.desc())

    pagination = db.paginate(
        query,
        page=page,
        per_page=30,
        error_out=False
    )

    urls = pagination.items

    # Total matching links
    total_links = query.count()

    # Total clicks of all matching links (not just current page)
    total_clicks = (
        query.with_entities(func.sum(URL.clicks)).scalar() or 0
    )

    return render_template(
        "dashboard.html",
        urls=urls,
        total_links=total_links,
        total_clicks=total_clicks,
        search=search,
        pagination=pagination
    )


@dashboard_bp.route("/delete/<int:id>")
def delete_url(id):

    url = URL.query.get_or_404(id)

    db.session.delete(url)
    db.session.commit()

    return redirect(url_for("dashboard.dashboard"))
