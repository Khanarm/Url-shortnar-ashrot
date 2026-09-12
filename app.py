from flask import (
    Flask,
    render_template
)

from config import Config

from routes.home import home_bp
from routes.dashboard import dashboard_bp
from routes.links import links_bp
from routes.api import api_bp
from routes.auth import auth_bp
from routes.admin import admin_bp

from mongo import client


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.config.from_object(Config)


# =========================================================
# SESSION CONFIGURATION
# =========================================================

# Flask session needs a secret key.
# Config.py me SECRET_KEY hona chahiye.
if not app.config.get("SECRET_KEY"):

    raise RuntimeError(
        "SECRET_KEY is missing. Please set SECRET_KEY in Config/environment."
    )


# Railway / HTTPS friendly session settings
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Use secure cookies when running on HTTPS
app.config["SESSION_COOKIE_SECURE"] = True

# Permanent session lifetime
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 30


# =========================================================
# MONGODB CONNECTION TEST
# =========================================================

try:

    client.admin.command("ping")

    print(
        "✅ MongoDB Connected Successfully"
    )

except Exception as e:

    print(
        "❌ MongoDB Connection Failed:",
        e
    )


# =========================================================
# BLUEPRINTS
# =========================================================

app.register_blueprint(
    home_bp
)

app.register_blueprint(
    dashboard_bp
)

app.register_blueprint(
    links_bp
)

app.register_blueprint(
    api_bp
)

app.register_blueprint(
    auth_bp
)

app.register_blueprint(
    admin_bp
)


# =========================================================
# 404 ERROR
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


# =========================================================
# TEST ROUTE
# =========================================================

@app.route("/test")
def test():

    return "Working"


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
    )
