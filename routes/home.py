from flask import Blueprint, render_template, request
from database import db
from models import URL
import random
import string

home_bp = Blueprint("home", __name__)


def generate_code(length=6):
    chars = string.ascii_letters + string.digits

    while True:
        code = "".join(random.choice(chars) for _ in range(length))

        if not URL.query.filter_by(short_code=code).first():
            return code


@home_bp.route("/", methods=["GET", "POST"])
def home():

    short_url = None

    if request.method == "POST":

        original_url = request.form.get("url")

        if original_url:

            code = generate_code()

            new_url = URL(
                original_url=original_url,
                short_code=code
            )

            db.session.add(new_url)
            db.session.commit()

            short_url = request.host_url + code

    return render_template(
        "index.html",
        short_url=short_url
  )
