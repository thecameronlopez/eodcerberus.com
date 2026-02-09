from flask import Blueprint, request
from flask_login import current_user, login_user, logout_user
from marshmallow import ValidationError as MarshmallowValidationError

from app.extensions import db, bcrypt
from app.handlers.errors.domain import PermissionDenied
from app.handlers.errors.validation import ValidationError as AppValidationError
from app.models import User
from app.schemas import user_login_schema, user_schema
from app.utils.responses import success


bp = Blueprint("auth", __name__)


@bp.post("/auth/login")
def login():
    try:
        data = user_login_schema.load(request.get_json() or {})
    except MarshmallowValidationError as err:
        raise AppValidationError(err.messages)

    email = data["email"].lower()
    password = data["password"]

    user = db.session.query(User).filter(User.email == email).first()
    if not user or user.terminated or not bcrypt.check_password_hash(user.password_hash, password):
        raise PermissionDenied("Invalid credentials.")

    login_user(user)
    return success("Login successful", {"user": user_schema.dump(user)})


@bp.post("/auth/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return success("Logout successful")


@bp.get("/auth/me")
def me():
    if not current_user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    return success(data={"user": user_schema.dump(current_user)})
