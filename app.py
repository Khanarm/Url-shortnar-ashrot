from flask import Flask, render_template
from config import Config
from database import db

from routes.home import home_bp
from routes.dashboard import dashboard_bp
from routes.links import links_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

# Register Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(links_bp)


# Custom 404 Error Page
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)

@app.route("/test")
def test():
    return "Working"
