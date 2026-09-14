from flask import (
    Blueprint,
    request,
    jsonify
)

from database import (
    urls,
    users
)

import random
import string
import secrets

from datetime import datetime


api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


def generate_code(length=6):

    chars = string.ascii_letters + string.digits

    while True:

        code = "".join(
            random.choice(chars)
            for _ in range(length)
        )

        if not urls.find_one({
            "short_code": code
        }):

            return code


def get_api_user():

    api_key = request.headers.get(
        "X-API-Key",
        ""
    ).strip()

    # Also allow query parameter
    if not api_key:

        api_key = request.args.get(
            "api_key",
            ""
        ).strip()

    if not api_key:

        return None

    return users.find_one({
        "api_key": api_key,
        "blocked": {
            "$ne": True
        }
    })


# ---------------------------------------------------------------------------
# Shortzy / AdLinkFly compatible endpoint
# ---------------------------------------------------------------------------
# Shortzy calls custom shortener domains using:
#   GET /api?api=<API_KEY>&url=<LONG_URL>
# and expects an AdLinkFly-style JSON response containing `shortenedUrl`.
# This endpoint keeps the existing /api/v1/shorten API untouched while making
# this service usable directly with the bot's existing Shortzy integration.
@api_bp.route(
    "",
    methods=["GET"]
)
def shortzy_compat():

    user = get_api_user()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid or missing API key."
        }), 401

    original_url = str(
        request.args.get("url", "")
    ).strip()

    if not original_url:
        return jsonify({
            "status": "error",
            "message": "URL is required."
        }), 400

    alias = str(
        request.args.get("alias", "")
    ).strip()

    if alias:
        if urls.find_one({"short_code": alias}):
            return jsonify({
                "status": "error",
                "message": "Alias already exists."
            }), 400
        code = alias
    else:
        code = generate_code()

    urls.insert_one({
        "original_url": original_url,
        "short_code": code,
        "alias": alias,
        "backup_tag": "",
        "clicks": 0,
        "owner_id": str(user["_id"]),
        "owner_username": user.get("username", ""),
        "created_at": datetime.utcnow()
    })

    base = request.host_url.rstrip("/")
    short_url = f"{base}/go/{code}"

    # AdLinkFly/Shortzy-compatible response.
    return jsonify({
        "status": "success",
        "shortenedUrl": short_url,
        "short_url": short_url,
        "short_code": code
    }), 200


@api_bp.route(
    "/v1/shorten",
    methods=["POST"]
)
def shorten_v1():

    user = get_api_user()

    if not user:

        return jsonify({
            "success": False,
            "message": "Invalid or missing API key."
        }), 401

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON body required."
        }), 400

    suffix = str(
        data.get(
            "suffix",
            ""
        )
    ).strip()

    backup_tag = str(
        data.get(
            "backup_tag",
            ""
        )
    ).strip()

    # -------------------------
    # Single URL
    # -------------------------

    if "url" in data:

        original_url = str(
            data.get(
                "url",
                ""
            )
        ).strip()

        if not original_url:

            return jsonify({
                "success": False,
                "message": "URL is required."
            }), 400

        alias = str(
            data.get(
                "alias",
                ""
            )
        ).strip()

        if alias:

            if urls.find_one({
                "short_code": alias
            }):

                return jsonify({
                    "success": False,
                    "message": "Alias already exists."
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

            "owner_id": str(
                user["_id"]
            ),

            "owner_username": user.get(
                "username",
                ""
            ),

            "created_at": datetime.utcnow()

        })

        base = request.host_url.rstrip("/")

        # IMPORTANT:
        # Website verification/redirect route is /go/<short_code>
        short_url = (
            f"{base}/go/{code}"
        )

        if suffix:

            short_url += f"/{suffix}"

        return jsonify({

            "success": True,

            "short_code": code,

            "short_url": short_url,

            "owner": user.get(
                "username",
                ""
            )

        })


    # -------------------------
    # Multiple URLs
    # -------------------------

    if "urls" in data:

        input_urls = data.get(
            "urls"
        )

        if not isinstance(
            input_urls,
            list
        ):

            return jsonify({
                "success": False,
                "message": "urls must be an array."
            }), 400

        results = []

        base = request.host_url.rstrip("/")

        for original_url in input_urls:

            original_url = str(
                original_url
            ).strip()

            if not original_url:

                continue

            code = generate_code()

            urls.insert_one({

                "original_url": original_url,

                "short_code": code,

                "alias": "",

                "backup_tag": backup_tag,

                "clicks": 0,

                "owner_id": str(
                    user["_id"]
                ),

                "owner_username": user.get(
                    "username",
                    ""
                ),

                "created_at": datetime.utcnow()

            })

            # IMPORTANT:
            # Use verification/redirect route
            short_url = f"{base}/go/{code}"

            if suffix:

                short_url += f"/{suffix}"

            results.append({

                "original_url": original_url,

                "short_code": code,

                "short_url": short_url

            })


        return jsonify({

            "success": True,

            "count": len(results),

            "results": results

        })


    return jsonify({

        "success": False,

        "message": "url or urls field required."

    }), 400


@api_bp.route(
    "/v1/me",
    methods=["GET"]
)
def me():

    user = get_api_user()

    if not user:

        return jsonify({
            "success": False,
            "message": "Invalid API key."
        }), 401

    return jsonify({

        "success": True,

        "username": user.get(
            "username",
            ""
        ),

        "today_earning": round(
            user.get(
                "today_earning",
                0
            ),
            6
        ),

        "total_earning": round(
            user.get(
                "total_earning",
                0
            ),
            6
        ),

        "available_balance": round(
            user.get(
                "available_balance",
                0
            ),
            6
        ),

        "total_withdrawals": user.get(
            "total_withdrawals",
            0
        ),

        "total_withdrawn": round(
            user.get(
                "total_withdrawn",
                0
            ),
            6
        )

    })


@api_bp.route("/test")
def test_api():

    return jsonify({
        "status": "API working"
    })
