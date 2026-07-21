from flask import Blueprint, render_template, request
from database import urls
import random
import string
from datetime import datetime

home_bp = Blueprint("home", __name__)


def generate_code(length=6):
    chars = string.ascii_letters + string.digits

    while True:
        code = "".join(random.choice(chars) for _ in range(length)) + "-alice"

        if urls.find_one({"short_code": code}) is None:
            return code


@home_bp.route("/", methods=["GET", "POST"])
def home():

    short_url = None
    error = None

    if request.method == "POST":

        original_url = request.form.get("url", "").strip()

        custom_alias = request.form.get(
            "custom_alias",
            ""
        ).strip()

        backup_tag = request.form.get(
            "backup_tag",
            ""
        ).strip()

        if original_url:

            if custom_alias:

                code = custom_alias + "-ckdrama"

                if urls.find_one({"short_code": code}):

                    error = "This alias is already taken."

            else:

                code = generate_code()

            if error is None:

                urls.insert_one({

                    "original_url": original_url,

                    "short_code": code,

                    "alias": custom_alias,

                    "backup_tag": backup_tag,

                    "clicks": 0,

                    "created_at": datetime.utcnow()

                })

                short_url = request.host_url + code

    return render_template(
        "index.html",
        short_url=short_url,
        error=error
    )


@home_bp.route("/about")
def about():
    return render_template("about.html")


@home_bp.route("/contact")
def contact():
    return render_template("contact.html")


@home_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@home_bp.route("/terms")
def terms():
    return render_template("terms.html")
