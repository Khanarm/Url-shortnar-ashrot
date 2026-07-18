import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_NAME = "database.db"

DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_NAME)

SECRET_KEY = "change-this-to-a-random-secret-key"
