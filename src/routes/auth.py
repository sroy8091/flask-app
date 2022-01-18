"""
Defines the blueprint for the login and register
"""
from datetime import datetime, timedelta

import jwt
from flask import Blueprint, jsonify, request

import config
from models import User
from util import token_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"], strict_slashes=False)
def register():
    """Register User."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    is_admin = data.get("is_admin")
    new_user = User.register(username, password, is_admin)
    if new_user:
        return jsonify({"message": "Registration successful."}), 201
    return jsonify({"message": "Invalid username or password."}), 400


@auth_bp.route("/login", methods=["POST"], strict_slashes=False)
def login():
    """Login User."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = User.get_user(username, password)
    if user:
        token = jwt.encode(
            {
                "username": user.username,
                "exp": datetime.utcnow()
                + timedelta(minutes=config.JWT_EXPIRATION_MINUTES),
            },
            config.SECRET_KEY,
        )
        return (
            jsonify({"message": "Login successful.", "token": token.decode("UTF-8")}),
            200,
        )
    return jsonify({"message": "Invalid username or password."}), 401


@auth_bp.route("/user_details", methods=["GET"], strict_slashes=False)
@token_required
def user_details(current_user):
    """Get User Details."""
    return jsonify({"username": current_user.username, "is_admin": current_user.is_admin})
