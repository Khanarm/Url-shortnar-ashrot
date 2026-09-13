from functools import wraps

from flask import (
    session,
    redirect,
    url_for,
    request
)

from database import users

from bson import ObjectId
from bson.errors import InvalidId


def get_current_user():

    user_id = session.get("user_id")

    if not user_id:
        return None

    try:
        user = users.find_one({
            "_id": ObjectId(str(user_id))
        })

    except (InvalidId, TypeError, ValueError):

        session.pop("user_id", None)
        session.pop("username", None)

        return None

    return user


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
                    next=request.path
                )
            )

        if user.get("blocked", False):

            session.clear()

            return redirect(
                url_for("auth.login")
            )

        return func(*args, **kwargs)

    return wrapper


def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not session.get("admin"):

            return redirect(
                url_for("admin.login")
            )

        return func(*args, **kwargs)

    return wrapper
