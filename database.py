from pymongo import MongoClient
from config import Config


client = MongoClient(Config.MONGO_URI)

db = client["url_shortener"]

urls = db["urls"]
users = db["users"]
withdrawals = db["withdrawals"]


# Useful indexes
try:
    users.create_index("username", unique=True)
    users.create_index("api_key", unique=True)

    urls.create_index("short_code", unique=True)

    withdrawals.create_index(
        [
            ("user_id", 1),
            ("created_at", -1)
        ]
    )

except Exception as e:
    print("Index warning:", e)
