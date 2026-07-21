import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")

    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb+srv://ahadansaridmk_db_user:575751an@cluster0.its13au.mongodb.net/?appName=Cluster0"
    )

    BASE_URL = os.getenv("BASE_URL", "database_name")
