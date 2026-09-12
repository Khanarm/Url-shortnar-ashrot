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
from datetime import datetime, timezone
from functools import wraps


# =========================================================
# AUTH BLUEPRINT
# =========================================================

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

    # Already ObjectId
    if isinstance(user_id, ObjectId):
        object_id = user_id

    else:

        try:
            object_id = ObjectId(str(user_id))

        except (InvalidId, TypeError, ValueError):

            session.pop("user_id", None)
            session.pop("username", None)

            return None

    user = users.find_one({
        "_id": object_id
    })

    # User no longer exists
    if not user:

        session.pop("user_id", None)
        session.pop("username", None)

        return None

    return user


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        user = get_current_user()

        if not user:

            session.pop("user_id", None)
            session.pop("username", None)

            return redirect(
                url_for(
                    "auth.login",
                    next=request.full_path
                )
            )

        # Blocked user
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

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not username or not email or not password:

            flash(
                "Username, Gmail ID and password are required.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        # -------------------------------------------------
        # USERNAME VALIDATION
        # -------------------------------------------------

        if not re.fullmatch(
            r"[a-z0-9_]{3,30}",
            username
        ):

            flash(
                "Username must be 3-30 characters and contain only letters, numbers and underscore.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        # -------------------------------------------------
        # GMAIL VALIDATION
        # -------------------------------------------------

        if not re.fullmatch(
            r"[a-z0-9._%+-]+@gmail\.com",
            email
        ):

            flash(
                "Please enter a valid Gmail ID.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        # -------------------------------------------------
        # PASSWORD VALIDATION
        # -------------------------------------------------

        if len(password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        # -------------------------------------------------
        # CHECK USERNAME
        # -------------------------------------------------

        existing_username = users.find_one({
            "username": username
        })

        if existing_username:

            flash(
                "Username already exists.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        # -------------------------------------------------
        # CHECK EMAIL
        # -------------------------------------------------

        existing_email = users.find_one({
            "email": email
        })

        if existing_email:

            flash(
                "This Gmail ID is already registered.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        # -------------------------------------------------
        # GENERATE API KEY
        # -------------------------------------------------

        api_key = generate_api_key()

        now = datetime.now(timezone.utc)

        today = now.strftime(
            "%Y-%m-%d"
        )

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        user = {

            "username": username,

            "email": email,

            "password": generate_password_hash(
                password
            ),

            "api_key": api_key,

            # ---------------------------------------------
            # EARNING
            # ---------------------------------------------

            "today_earning": 0.0,

            "total_earning": 0.0,

            "available_balance": 0.0,

            # ---------------------------------------------
            # WITHDRAWAL
            # ---------------------------------------------

            "total_withdrawals": 0,

            "total_withdrawn": 0.0,

            # ---------------------------------------------
            # ACCOUNT
            # ---------------------------------------------

            "blocked": False,

            "created_at": now,

            "last_earning_date": today
        }

        # -------------------------------------------------
        # INSERT INTO MONGODB
        # -------------------------------------------------

        try:

            result = users.insert_one(user)

        except Exception as e:

            print(
                "Registration database error:",
                repr(e)
            )

            flash(
                "Unable to create account. Please try again.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        # -------------------------------------------------
        # LOGIN NEW USER
        # -------------------------------------------------

        session.clear()

        # IMPORTANT:
        # MongoDB ObjectId is converted to string
        # before storing inside Flask session.

        session["user_id"] = str(
            result.inserted_id
        )

        session["username"] = username

        # Make session permanent for this browser
        session.permanent = True

        # -------------------------------------------------
        # DASHBOARD
        # -------------------------------------------------

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

        # -------------------------------------------------
        # REQUIRED
        # -------------------------------------------------

        if not username or not password:

            flash(
                "Username and password are required.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        # -------------------------------------------------
        # FIND USER
        # -------------------------------------------------

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

        # -------------------------------------------------
        # PASSWORD
        # -------------------------------------------------

        stored_password = user.get(
            "password",
            ""
        )

        if not stored_password:

            flash(
                "Account password is not configured.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        try:

            password_correct = check_password_hash(
                stored_password,
                password
            )

        except Exception as e:

            print(
                "Password verification error:",
                repr(e)
            )

            password_correct = False

        if not password_correct:

            flash(
                "Invalid username or password.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        # -------------------------------------------------
        # BLOCKED USER
        # -------------------------------------------------

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

        # -------------------------------------------------
        # CREATE SESSION
        # -------------------------------------------------

        session.clear()

        session["user_id"] = str(
            user["_id"]
        )

        session["username"] = user.get(
            "username",
            ""
        )

        session.permanent = True

        # -------------------------------------------------
        # DASHBOARD
        # -------------------------------------------------

        return redirect(
            url_for("dashboard.dashboard")
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route(
    "/logout"
)
def logout():

    session.clear()

    return redirect(
        url_for("home.home")
    )
