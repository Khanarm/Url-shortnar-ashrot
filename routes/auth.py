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

from bson import ObjectId
from bson.errors import InvalidId

import secrets
import re
from datetime import datetime


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# =========================================================
# API KEY GENERATOR
# =========================================================

def generate_api_key():

    while True:

        key = "ask_" + secrets.token_urlsafe(32)

        existing = users.find_one({
            "api_key": key
        })

        if not existing:
            return key


# =========================================================
# GET CURRENT USER
# =========================================================

def get_current_user():

    user_id = session.get("user_id")

    if not user_id:
        return None

    # Convert session string back to MongoDB ObjectId
    try:

        object_id = ObjectId(user_id)

    except (InvalidId, TypeError):

        session.pop("user_id", None)

        return None

    user = users.find_one({
        "_id": object_id
    })

    return user


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(func):

    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):

        user = get_current_user()

        if not user:

            session.pop("user_id", None)

            return redirect(
                url_for(
                    "auth.login",
                    next=request.path
                )
            )

        # Blocked user cannot access dashboard
        if user.get("blocked", False):

            session.clear()

            flash(
                "Your account has been blocked.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        return func(*args, **kwargs)

    return wrapper


# =========================================================
# ADMIN REQUIRED
# =========================================================

def admin_required(func):

    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not session.get("admin"):

            return redirect(
                url_for("admin.login")
            )

        return func(*args, **kwargs)

    return wrapper


# =========================================================
# REGISTER
# =========================================================

@auth_bp.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    # Already logged in
    if get_current_user():

        return redirect(
            url_for("dashboard.dashboard")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # -----------------------------------------
        # Validation
        # -----------------------------------------

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
                "Username must contain only letters, numbers and underscore.",
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

        # -----------------------------------------
        # Check existing username
        # -----------------------------------------

        existing_user = users.find_one({
            "username": username
        })

        if existing_user:

            flash(
                "Username already exists.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        # -----------------------------------------
        # Generate API key
        # -----------------------------------------

        api_key = generate_api_key()

        now = datetime.utcnow()

        today = now.strftime(
            "%Y-%m-%d"
        )

        # -----------------------------------------
        # Create user
        # -----------------------------------------

        user = {

            "username": username,

            "password": generate_password_hash(
                password
            ),

            "api_key": api_key,

            # Earning
            "today_earning": 0.0,

            "total_earning": 0.0,

            "available_balance": 0.0,

            # Withdrawal
            "total_withdrawals": 0,

            "total_withdrawn": 0.0,

            # Account
            "blocked": False,

            "created_at": now,

            "last_earning_date": today
        }

        try:

            result = users.insert_one(user)

        except Exception as e:

            print(
                "Registration database error:",
                e
            )

            flash(
                "Unable to create account. Please try again.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        # -----------------------------------------
        # Login newly registered user
        # -----------------------------------------

        session.clear()

        # Store ObjectId as string in session
        session["user_id"] = str(
            result.inserted_id
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # Already logged in
    if get_current_user():

        return redirect(
            url_for("dashboard.dashboard")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # -----------------------------------------
        # Find user
        # -----------------------------------------

        user = users.find_one({
            "username": username
        })

        if not user:

            flash(
                "Invalid username or password.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        # -----------------------------------------
        # Check password
        # -----------------------------------------

        stored_password = user.get(
            "password",
            ""
        )

        if not check_password_hash(
            stored_password,
            password
        ):

            flash(
                "Invalid username or password.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        # -----------------------------------------
        # Check blocked status
        # -----------------------------------------

        if user.get(
            "blocked",
            False
        ):

            flash(
                "Your account has been blocked.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        # -----------------------------------------
        # Create session
        # -----------------------------------------

        session.clear()

        session["user_id"] = str(
            user["_id"]
        )

        # Optional username session
        session["username"] = user.get(
            "username",
            ""
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home.home")
    )
