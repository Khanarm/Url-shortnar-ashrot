import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")

    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/url_shortener?retryWrites=true&w=majority"
    )

    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
