from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash
)

from database import users, withdrawals

from auth import login_required, get_current_user

from config import Config

from datetime import datetime


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


# =========================================================
# DASHBOARD
# =========================================================

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    user = get_current_user()

    if not user:
        return redirect(
            url_for("auth.login")
        )

    today = datetime.utcnow().strftime("%Y-%m-%d")

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


# =========================================================
# USER PROFILE
# =========================================================

@dashboard_bp.route(
    "/profile",
    methods=["GET", "POST"]
)
@login_required
def profile():

    user = get_current_user()

    if not user:
        return redirect(
            url_for("auth.login")
        )

    if request.method == "POST":

        mobile = request.form.get(
            "mobile",
            ""
        ).strip()

        bank_name = request.form.get(
            "bank_name",
            ""
        ).strip()

        account_holder = request.form.get(
            "account_holder",
            ""
        ).strip()

        account_number = request.form.get(
            "account_number",
            ""
        ).strip()

        ifsc = request.form.get(
            "ifsc",
            ""
        ).strip().upper()

        branch = request.form.get(
            "branch",
            ""
        ).strip()

        upi_id = request.form.get(
            "upi_id",
            ""
        ).strip()

        # -------------------------------------------------
        # REQUIRED BANK DETAILS
        # -------------------------------------------------

        if not mobile:
            flash(
                "Mobile number is required.",
                "error"
            )

            return redirect(
                url_for("dashboard.profile")
            )

        if not bank_name:
            flash(
                "Bank name is required.",
                "error"
            )

            return redirect(
                url_for("dashboard.profile")
            )

        if not account_holder:
            flash(
                "Account holder name is required.",
                "error"
            )

            return redirect(
                url_for("dashboard.profile")
            )

        if not account_number:
            flash(
                "Account number is required.",
                "error"
            )

            return redirect(
                url_for("dashboard.profile")
            )

        if not ifsc:
            flash(
                "IFSC code is required.",
                "error"
            )

            return redirect(
                url_for("dashboard.profile")
            )

        if not branch:
            flash(
                "Branch name is required.",
                "error"
            )

            return redirect(
                url_for("dashboard.profile")
            )

        # -------------------------------------------------
        # MOBILE VALIDATION
        # -------------------------------------------------

        mobile_clean = mobile.replace(
            " ",
            ""
        )

        if not mobile_clean.isdigit() or len(mobile_clean) != 10:

            flash(
                "Please enter a valid 10 digit mobile number.",
                "error"
            )

            return redirect(
                url_for("dashboard.profile")
            )

        # -------------------------------------------------
        # ACCOUNT NUMBER VALIDATION
        # -------------------------------------------------

        account_clean = account_number.replace(
            " ",
            ""
        )

        if not account_clean.isdigit():

            flash(
                "Account number must contain only numbers.",
                "error"
            )

            return redirect(
                url_for("dashboard.profile")
            )

        if len(account_clean) < 6 or len(account_clean) > 20:

            flash(
                "Please enter a valid bank account number.",
                "error"
            )

            return redirect(
                url_for("dashboard.profile")
            )

        # -------------------------------------------------
        # IFSC VALIDATION
        # -------------------------------------------------

        if len(ifsc) != 11:

            flash(
                "IFSC code must be 11 characters.",
                "error"
            )

            return redirect(
                url_for("dashboard.profile")
            )

        # -------------------------------------------------
        # SAVE BANK DETAILS
        # -------------------------------------------------

        bank_details = {

            "mobile": mobile_clean,

            "bank_name": bank_name,

            "account_holder": account_holder,

            "account_number": account_clean,

            "ifsc": ifsc,

            "branch": branch,

            "upi_id": upi_id
        }

        users.update_one(
            {
                "_id": user["_id"]
            },
            {
                "$set": {
                    "bank_details": bank_details
                }
            }
        )

        flash(
            "Bank account details saved successfully.",
            "success"
        )

        return redirect(
            url_for("dashboard.profile")
        )

    return render_template(
        "profile.html",
        user=user
    )


# =========================================================
# WITHDRAW
# =========================================================

@dashboard_bp.route(
    "/withdraw",
    methods=["POST"]
)
@login_required
def withdraw():

    user = get_current_user()

    if not user:
        return redirect(
            url_for("auth.login")
        )

    # -------------------------------------------------
    # AMOUNT
    # -------------------------------------------------

    try:

        amount = float(
            request.form.get(
                "amount",
                "0"
            )
        )

    except (ValueError, TypeError):

        amount = 0

    # -------------------------------------------------
    # BASIC VALIDATION
    # -------------------------------------------------

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

    # -------------------------------------------------
    # BANK DETAILS
    # -------------------------------------------------

    bank = user.get(
        "bank_details",
        {}
    )

    required_fields = [
        "mobile",
        "bank_name",
        "account_holder",
        "account_number",
        "ifsc",
        "branch"
    ]

    missing = False

    for field in required_fields:

        if not str(
            bank.get(field, "")
        ).strip():

            missing = True
            break

    if missing:

        flash(
            "Please complete your Bank Account Details in your Profile before requesting withdrawal.",
            "error"
        )

        return redirect(
            url_for("dashboard.profile")
        )

    # -------------------------------------------------
    # ATOMIC BALANCE DEDUCTION
    # -------------------------------------------------

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

    # -------------------------------------------------
    # SAVE WITHDRAWAL REQUEST
    # -------------------------------------------------

    withdrawals.insert_one({

        "user_id": str(
            user["_id"]
        ),

        "username": user.get(
            "username",
            ""
        ),

        "amount": amount,

        # Bank details snapshot
        "bank_details": {
            "mobile": bank.get(
                "mobile",
                ""
            ),

            "bank_name": bank.get(
                "bank_name",
                ""
            ),

            "account_holder": bank.get(
                "account_holder",
                ""
            ),

            "account_number": bank.get(
                "account_number",
                ""
            ),

            "ifsc": bank.get(
                "ifsc",
                ""
            ),

            "branch": bank.get(
                "branch",
                ""
            ),

            "upi_id": bank.get(
                "upi_id",
                ""
            )
        },

        "status": "PENDING",

        "created_at": datetime.utcnow(),

        "processed_at": None
    })

    flash(
        "Withdrawal request submitted successfully.",
        "success"
    )

    return redirect(
        url_for("dashboard.dashboard")
    )
