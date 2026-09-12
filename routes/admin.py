from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import check_password_hash

from database import (
    users,
    withdrawals
)

from config import Config

from auth import admin_required

from datetime import datetime


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


@admin_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        )

        password = request.form.get(
            "password",
            ""
        )

        if (
            username == Config.ADMIN_USERNAME
            and password == Config.ADMIN_PASSWORD
        ):

            session.clear()

            session["admin"] = True

            return redirect(
                url_for("admin.dashboard")
            )

        flash(
            "Invalid admin credentials.",
            "error"
        )

    return render_template(
        "admin_login.html"
    )


@admin_bp.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect(
        url_for("admin.login")
    )


@admin_bp.route("/")
@admin_bp.route("/dashboard")
@admin_required
def dashboard():

    total_users = users.count_documents({})

    pending_withdrawals = withdrawals.count_documents({
        "status": "PENDING"
    })

    paid_withdrawals = withdrawals.count_documents({
        "status": "PAID"
    })

    rejected_withdrawals = withdrawals.count_documents({
        "status": "REJECTED"
    })

    pipeline = [

        {
            "$group": {
                "_id": None,
                "total": {
                    "$sum": "$total_earning"
                },
                "today": {
                    "$sum": "$today_earning"
                },
                "balance": {
                    "$sum": "$available_balance"
                },
                "withdrawn": {
                    "$sum": "$total_withdrawn"
                }
            }
        }

    ]

    stats = list(
        users.aggregate(pipeline)
    )

    stats = stats[0] if stats else {}

    user_list = list(
        users.find({})
        .sort(
            "created_at",
            -1
        )
        .limit(100)
    )

    return render_template(
        "admin.html",

        total_users=total_users,

        pending_withdrawals=pending_withdrawals,

        paid_withdrawals=paid_withdrawals,

        rejected_withdrawals=rejected_withdrawals,

        total_earning=stats.get(
            "total",
            0
        ),

        today_earning=stats.get(
            "today",
            0
        ),

        total_balance=stats.get(
            "balance",
            0
        ),

        total_withdrawn=stats.get(
            "withdrawn",
            0
        ),

        users=user_list
    )


@admin_bp.route("/withdrawals")
@admin_required
def withdrawal_list():

    data = list(
        withdrawals.find({})
        .sort(
            "created_at",
            -1
        )
        .limit(200)
    )

    return render_template(
        "admin_withdrawals.html",
        withdrawals=data
    )


@admin_bp.route(
    "/withdrawal/<withdrawal_id>/accept",
    methods=["POST"]
)
@admin_required
def accept_withdrawal(withdrawal_id):

    withdrawal = withdrawals.find_one({
        "_id": __import__(
            "bson"
        ).ObjectId(withdrawal_id)
    })

    if not withdrawal:

        flash(
            "Withdrawal not found.",
            "error"
        )

        return redirect(
            url_for("admin.withdrawal_list")
        )

    # Only PENDING can be accepted
    result = withdrawals.update_one(
        {
            "_id": withdrawal["_id"],
            "status": "PENDING"
        },
        {
            "$set": {
                "status": "PAID",
                "processed_at": datetime.utcnow()
            }
        }
    )

    if result.modified_count == 1:

        users.update_one(
            {
                "_id": __import__(
                    "bson"
                ).ObjectId(
                    withdrawal["user_id"]
                )
            },
            {
                "$inc": {
                    "total_withdrawals": 1,
                    "total_withdrawn": withdrawal["amount"]
                }
            }
        )

        flash(
            "Withdrawal marked as PAID.",
            "success"
        )

    return redirect(
        url_for("admin.withdrawal_list")
    )


@admin_bp.route(
    "/withdrawal/<withdrawal_id>/reject",
    methods=["POST"]
)
@admin_required
def reject_withdrawal(withdrawal_id):

    from bson import ObjectId

    withdrawal = withdrawals.find_one({
        "_id": ObjectId(withdrawal_id)
    })

    if not withdrawal:

        flash(
            "Withdrawal not found.",
            "error"
        )

        return redirect(
            url_for("admin.withdrawal_list")
        )

    # Only PENDING can be rejected.
    # This prevents double refund.
    result = withdrawals.update_one(
        {
            "_id": withdrawal["_id"],
            "status": "PENDING"
        },
        {
            "$set": {
                "status": "REJECTED",
                "processed_at": datetime.utcnow()
            }
        }
    )

    if result.modified_count == 1:

        # Return amount to available balance
        users.update_one(
            {
                "_id": ObjectId(
                    withdrawal["user_id"]
                )
            },
            {
                "$inc": {
                    "available_balance": withdrawal["amount"]
                }
            }
        )

        flash(
            "Withdrawal rejected and balance returned.",
            "success"
        )

    return redirect(
        url_for("admin.withdrawal_list")
    )
