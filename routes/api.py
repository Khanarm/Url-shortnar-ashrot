from flask import Blueprint, request, jsonify
from database import db
from models import URL
import random
import string

api_bp = Blueprint("api", __name__, url_prefix="/api")


def generate_code(length=6):
    chars = string.ascii_letters + string.digits

    while True:
        code = "".join(random.choice(chars) for _ in range(length))

        exists = URL.query.filter_by(short_code=code).first()

        if not exists:
            return code


@api_bp.route("/shorten", methods=["POST"])
def shorten_api():

    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({
            "success": False,
            "message": "URL missing"
        }), 400


    original_url = data["url"]

    code = generate_code()


    new_url = URL(
        original_url=original_url,
        short_code=code
    )


    db.session.add(new_url)
    db.session.commit()


    return jsonify({
        "success": True,
        "short_code": code,
        "short_url": request.host_url + code
    })

@api_bp.route("/test")
def test_api():
    return jsonify({
        "status": "API working"
    })
