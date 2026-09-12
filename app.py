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


app = Flask(__name__)

app.config.from_object(Config)


# MongoDB connection test
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


# Blueprints
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


@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


@app.route("/test")
def test():

    return "Working"


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )
