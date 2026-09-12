from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash
)

from database import (
    users,
    withdrawals
)

from auth import login_required, get_current_user

from config import Config

from datetime import datetime

from bson import ObjectId


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    user = get_current_user()

    if not user:

        return redirect(
            url_for("auth.login")
        )

    today = datetime.utcnow().strftime(
        "%Y-%m-%d"
    )

    last_date = user.get(
        "last_earning_date"
    )

    today_earning = float(
        user.get("today_earning", 0)
    )

    # Reset today's earning when a new day starts
    if last_date != today:

        users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "today_earning": 0.0,
                    "last_earning_date": today
                }
            }
        )

        today_earning = 0.0

        user["today_earning"] = 0.0

    history = list(
        withdrawals.find({
            "user_id": str(user["_id"])
        })
        .sort(
            "created_at",
            -1
        )
        .limit(20)
    )

    return render_template(
        "dashboard.html",
        user=user,
        today_earning=today_earning,
        min_withdraw=Config.MIN_WITHDRAW_USDT,
        history=history
    )


@dashboard_bp.route(
    "/withdraw",
    methods=["POST"]
)
@login_required
def withdraw():

    user = get_current_user()

    try:

        amount = float(
            request.form.get(
                "amount",
                "0"
            )
        )

    except ValueError:

        amount = 0

    wallet = request.form.get(
        "wallet",
        ""
    ).strip()

    network = request.form.get(
        "network",
        "TRC20"
    ).strip().upper()

    if amount <= 0:

        flash(
            "Invalid withdrawal amount.",
            "error"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    if amount < Config.MIN_WITHDRAW_USDT:

        flash(
            f"Minimum withdrawal is {Config.MIN_WITHDRAW_USDT} USDT.",
            "error"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    if not wallet:

        flash(
            "Wallet address is required.",
            "error"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    # Atomic balance deduction.
    # This prevents double withdrawal.
    result = users.update_one(
        {
            "_id": user["_id"],
            "available_balance": {
                "$gte": amount
            }
        },
        {
            "$inc": {
                "available_balance": -amount
            }
        }
    )

    if result.modified_count != 1:

        flash(
            "Insufficient available balance.",
            "error"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    withdrawals.insert_one({

        "user_id": str(user["_id"]),

        "username": user.get(
            "username",
            ""
        ),

        "amount": amount,

        "wallet": wallet,

        "network": network,

        "status": "PENDING",

        "created_at": datetime.utcnow(),

        "processed_at": None

    })

    flash(
        "Withdrawal request submitted.",
        "success"
    )

    return redirect(
        url_for("dashboard.dashboard")
    )
