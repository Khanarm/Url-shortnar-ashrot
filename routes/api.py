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

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    # Default suffix
    suffix = data.get("suffix", "ckdrama").strip()

    # =========================
    # Single URL
    # =========================
    if "url" in data:

        original_url = data["url"].strip()
        alias = data.get("alias", "").strip()

        if alias:
            exists = URL.query.filter_by(short_code=alias).first()

            if exists:
                return jsonify({
                    "success": False,
                    "message": "Alias already exists"
                }), 400

            code = alias

        else:
            code = generate_code()

        new_url = URL(
            original_url=original_url,
            short_code=code
        )

        db.session.add(new_url)
        db.session.commit()

        short_url = (
            request.host_url.rstrip("/")
            + "/"
            + code
            + "/"
            + suffix
        )

        return jsonify({
            "success": True,
            "short_code": code,
            "short_url": short_url
        })

    # =========================
    # Multiple URLs
    # =========================
    elif "urls" in data:

        urls = data["urls"]

        if not isinstance(urls, list):
            return jsonify({
                "success": False,
                "message": "urls must be a list"
            }), 400

        results = []

        for original_url in urls:

            code = generate_code()

            new_url = URL(
                original_url=original_url.strip(),
                short_code=code
            )

            db.session.add(new_url)

            results.append({
                "original_url": original_url,
                "short_code": code,
                "short_url": (
                    request.host_url.rstrip("/")
                    + "/"
                    + code
                    + "/"
                    + suffix
                )
            })

        db.session.commit()

        return jsonify({
            "success": True,
            "count": len(results),
            "results": results
        })

    return jsonify({
        "success": False,
        "message": "url or urls field required"
    }), 400


@api_bp.route("/test")
def test_api():
    return jsonify({
        "status": "API working"
    })
