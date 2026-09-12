from functools import wraps

from flask import (
    session,
    redirect,
    url_for,
    request
)

from database import users


def get_current_user():

    user_id = session.get("user_id")

    if not user_id:
        return None

    user = users.find_one({
        "_id": user_id
    })

    return user


def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not session.get("user_id"):
            return redirect(
                url_for(
                    "auth.login",
                    next=request.path
                )
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
