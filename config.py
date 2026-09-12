import os


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-secret-key"
    )

    MONGO_URI = os.getenv(
        "MONGO_URI",
        ""
    )

    BASE_URL = os.getenv(
        "BASE_URL",
        "https://ashort.in"
    )

    ADMIN_USERNAME = os.getenv(
        "ADMIN_USERNAME",
        "admin"
    )

    ADMIN_PASSWORD = os.getenv(
        "ADMIN_PASSWORD",
        "change-admin-password"
    )

    # Earning per successful completed visit
    EARNING_PER_VISIT_USDT = float(
        os.getenv(
            "EARNING_PER_VISIT_USDT",
            "0.002"
        )
    )

    MIN_WITHDRAW_USDT = float(
        os.getenv(
            "MIN_WITHDRAW_USDT",
            "10"
        )
    )
