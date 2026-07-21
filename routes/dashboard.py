from flask import Blueprint, render_template, request, redirect, url_for
from database import urls
from bson import ObjectId

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/dashboard")
def dashboard():

    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)

    per_page = 30

    query = {}

    if search:
        query = {
            "$or": [
                {
                    "original_url": {
                        "$regex": search,
                        "$options": "i"
                    }
                },
                {
                    "short_code": {
                        "$regex": search,
                        "$options": "i"
                    }
                },
                {
                    "alias": {
                        "$regex": search,
                        "$options": "i"
                    }
                },
                {
                    "backup_tag": {
                        "$regex": search,
                        "$options": "i"
                    }
                }
            ]
        }

    total_links = urls.count_documents(query)

    total_clicks = 0

    for item in urls.find(query):
        total_clicks += item.get("clicks", 0)

    total_pages = (
        (total_links + per_page - 1)
        // per_page
    )

    data = list(
        urls.find(query)
        .sort("created_at", -1)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )

    pagination = {
        "page": page,
        "pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_num": page - 1,
        "next_num": page + 1
    }

    return render_template(
        "dashboard.html",
        urls=data,
        total_links=total_links,
        total_clicks=total_clicks,
        search=search,
        pagination=pagination
    )


@dashboard_bp.route("/delete/<id>")
def delete_url(id):

    urls.delete_one(
        {
            "_id": ObjectId(id)
        }
    )

    return redirect(
        url_for("dashboard.dashboard")
    )
