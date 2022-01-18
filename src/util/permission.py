from functools import wraps

import jwt
from flask import jsonify, request

import config
from models import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if "Authorization" in request.headers:
            token = request.headers["Authorization"]
        # return 401 if token is not passed
        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token.split(" ")[1], config.SECRET_KEY)
            current_user = User.query.filter_by(username=data["username"], is_active=True).first()
        except Exception:
            return jsonify({"message": "Invalid token"}), 403
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated
