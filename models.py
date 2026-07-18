from database import db
from flask import redirect
from models import URL


class URL(db.Model):
    __tablename__ = "urls"

    id = db.Column(db.Integer, primary_key=True)

    original_url = db.Column(db.Text, nullable=False)

    short_code = db.Column(db.String(10), unique=True, nullable=False)

    clicks = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

@app.route("/<short_code>")
def redirect_url(short_code):

    url = URL.query.filter_by(short_code=short_code).first()

    if url:
        url.clicks += 1
        db.session.commit()

        return redirect(url.original_url)

    return "Link not found", 404
