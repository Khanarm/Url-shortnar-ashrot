from flask import Flask
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

if __name__ == "__main__":
    app.run(debug=True)
