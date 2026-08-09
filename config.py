import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")

    MONGO_URI = os.getenv(
        "MONGO_URI",
        ""
    )

    BASE_URL = os.getenv("BASE_URL", "database_name")
