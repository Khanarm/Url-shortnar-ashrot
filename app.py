import os

from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

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
# RAILWAY / PROXY SUPPORT
# =========================================================

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1
)


# =========================================================
# SESSION CONFIGURATION
# =========================================================

app.config["SESSION_COOKIE_NAME"] = "ashort_session"

app.config["SESSION_COOKIE_HTTPONLY"] = True

app.config["SESSION_COOKIE_SECURE"] = True

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config["SESSION_COOKIE_PATH"] = "/"

app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 30


# =========================================================
# MONGODB CONNECTION TEST
# =========================================================

try:

    client.admin.command("ping")

    print("✅ MongoDB Connected Successfully")

except Exception as e:

    print(
        "❌ MongoDB Connection Failed:",
        repr(e)
    )


# =========================================================
# BLUEPRINTS
# =========================================================

app.register_blueprint(home_bp)

app.register_blueprint(dashboard_bp)

app.register_blueprint(links_bp)

app.register_blueprint(api_bp)

app.register_blueprint(auth_bp)

app.register_blueprint(admin_bp)


# =========================================================
# 404
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


# =========================================================
# TEST
# =========================================================

@app.route("/test")
def test():

    return "Working"


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            8000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
