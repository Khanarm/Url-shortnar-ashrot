from flask import Blueprint, request, jsonify
from database import db
from models import URL
import random
import string

api_bp = Blueprint("api", __name__, url_prefix="/api")


def generate_code(length=6):
    chars = string.ascii_letters + string.digits

    while True:
        code = "".join(
            random.choice(chars)
            for _ in range(length)
        )

        exists = URL.query.filter_by(short_code=code).first()

        if not exists:
            return code


@api_bp.route("/shorten", methods=["POST"])
def shorten_api():

    print("=" * 60)
    print("NEW API REQUEST")

    data = request.get_json()
    print("REQUEST DATA:", data)

    if not data or "url" not in data:
        print("ERROR: URL missing")
        return jsonify({
            "success": False,
            "message": "URL missing"
        }), 400

    original_url = data["url"].strip()
    alias = data.get("alias", "").strip()

    print("ORIGINAL URL:", original_url)
    print("ALIAS:", alias)

    if alias:
        print("CHECKING ALIAS...")

        exists = URL.query.filter_by(short_code=alias).first()

        print("ALIAS EXISTS:", exists)

        if exists:
            print("ALIAS ALREADY EXISTS")

            return jsonify({
                "success": False,
                "message": "Alias already exists"
            }), 400

        code = alias
        print("USING CUSTOM ALIAS:", code)

    else:
        print("NO ALIAS, GENERATING RANDOM CODE")
        code = generate_code()

    print("FINAL SHORT CODE:", code)

    new_url = URL(
        original_url=original_url,
        short_code=code
    )

    print("ADDING TO DATABASE...")
    db.session.add(new_url)
    db.session.commit()
    print("DATABASE COMMIT SUCCESS")

    short_url = request.host_url.rstrip("/") + "/" + code

    print("RETURN SHORT URL:", short_url)
    print("=" * 60)

    return jsonify({
        "success": True,
        "short_code": code,
        "short_url": short_url
    })


@api_bp.route("/test")
def test_api():
    print("TEST API CALLED")
    return jsonify({
        "status": "API working"
    })
