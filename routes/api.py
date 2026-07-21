from flask import Blueprint, request, jsonify
from database import urls
import random
import string
from datetime import datetime

api_bp = Blueprint("api", __name__, url_prefix="/api")


def generate_code(length=6):
    chars = string.ascii_letters + string.digits

    while True:
        code = "".join(random.choice(chars) for _ in range(length))

        if urls.find_one({"short_code": code}) is None:
            return code


@api_bp.route("/shorten", methods=["POST"])
def shorten_api():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    suffix = data.get("suffix", "ckdrama").strip()

    backup_tag = data.get("backup_tag", "").strip()

    # ==========================
    # Single URL
    # ==========================
    if "url" in data:

        original_url = data["url"].strip()

        alias = data.get("alias", "").strip()

        if alias:

            if urls.find_one({"short_code": alias}):

                return jsonify({
                    "success": False,
                    "message": "Alias already exists"
                }), 400

            code = alias

        else:

            code = generate_code()

        urls.insert_one({

            "original_url": original_url,

            "short_code": code,

            "alias": alias,

            "backup_tag": backup_tag,

            "clicks": 0,

            "created_at": datetime.utcnow()

        })

        return jsonify({

            "success": True,

            "short_code": code,

            "short_url": request.host_url.rstrip("/") + "/" + code + "/" + suffix

        })

    # ==========================
    # Multiple URLs
    # ==========================
    elif "urls" in data:

        results = []

        for original_url in data["urls"]:

            code = generate_code()

            urls.insert_one({

                "original_url": original_url.strip(),

                "short_code": code,

                "alias": "",

                "backup_tag": backup_tag,

                "clicks": 0,

                "created_at": datetime.utcnow()

            })

            results.append({

                "original_url": original_url,

                "short_code": code,

                "short_url": request.host_url.rstrip("/") + "/" + code + "/" + suffix

            })

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
