from database import db


class URL(db.Model):
    __tablename__ = "urls"

    id = db.Column(db.Integer, primary_key=True)

    original_url = db.Column(db.Text, nullable=False)

    short_code = db.Column(db.String(10), unique=True, nullable=False)

    clicks = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
