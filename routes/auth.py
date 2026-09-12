from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import users

import secrets
import re
from datetime import datetime


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


def generate_api_key():

    while True:

        key = "ask_" + secrets.token_urlsafe(32)

        if not users.find_one({
            "api_key": key
        }):
            return key


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:

            flash(
                "Username and password are required.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        if not re.match(
            r"^[a-zA-Z0-9_]{3,30}$",
            username
        ):

            flash(
                "Username can contain only letters, numbers and underscore.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        if len(password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        if users.find_one({
            "username": username
        }):

            flash(
                "Username already exists.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        user = {

            "username": username,

            "password": generate_password_hash(
                password
            ),

            "api_key": generate_api_key(),

            "today_earning": 0.0,

            "total_earning": 0.0,

            "available_balance": 0.0,

            "total_withdrawals": 0,

            "total_withdrawn": 0.0,

            "created_at": datetime.utcnow(),

            "last_earning_date": datetime.utcnow().strftime(
                "%Y-%m-%d"
            )
        }

        result = users.insert_one(user)

        session.clear()

        session["user_id"] = str(
            result.inserted_id
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    return render_template(
        "register.html"
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = users.find_one({
            "username": username
        })

        if not user or not check_password_hash(
            user["password"],
            password
        ):

            flash(
                "Invalid username or password.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        if user.get("blocked", False):

            flash(
                "Your account has been blocked.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        session.clear()

        session["user_id"] = str(
            user["_id"]
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    return render_template(
        "login.html"
    )


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home.home")
    )
