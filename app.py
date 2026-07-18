from flask import Flask, render_template, request, redirect
from config import Config
from database import db
from models import URL
import string
import random

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@app.route("/", methods=["GET", "POST"])
def home():
    short_url = None

    if request.method == "POST":
        original_url = request.form.get("url")

        code = generate_code()

        new_url = URL(
            original_url=original_url,
            short_code=code
        )

        db.session.add(new_url)
        db.session.commit()

        short_url = request.host_url + code

    return render_template("index.html", short_url=short_url)


@app.route("/<short_code>")
def redirect_url(short_code):

    url = URL.query.filter_by(short_code=short_code).first()

    if url:
        url.clicks += 1
        db.session.commit()

        return redirect(url.original_url)

    return "Link not found", 404


if __name__ == "__main__":
    app.run(debug=True)
