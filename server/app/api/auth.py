from flask import Blueprint, jsonify, request, current_app
from app.models import Users, EOD
from app.extensions import db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user

authorizer = Blueprint("auth", __name__)

@authorizer.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    first_name = data.get("first_name").strip().title()
    last_name = data.get("last_name").strip().title()
    email = data.get("email").lower()
    department = data.get("department", "").strip().lower()
    is_admin = data.get("is_admin")
    pw = data.get("pw")
    pw2 = data.get("pw2")
    
    required = ["first_name", "last_name", "email", "pw", "pw2"]
    if not all(data.get(f) for f in required):
        return jsonify(success=False, message="Missing required fields."), 400
    
    if pw != pw2:
        return jsonify(success=False, message="Passwords do not match, please check inputs and try again."), 422
    
    if Users.query.filter_by(email=email).first():
        return jsonify(success=False, message="Email already in use."), 409
    
    new_user = Users(
        first_name=first_name,
        last_name=last_name,
        email=email,
        department=department,
        is_admin=is_admin,
        password_hash=bcrypt.generate_password_hash(pw).decode("utf-8")
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        current_app.logger.info(f"{new_user.first_name} has been registered to Cerberus")
        return jsonify(success=True, message=f"New user {new_user.first_name} has been registered!"), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[REGISTRATION ERROR]: {e}")
        return jsonify(success=False, message="There was an error when registering new user."), 500
    
    
@authorizer.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    pw = data.get("password")
    
    user = Users.query.filter_by(email=email).first()
    if not user:
        current_app.logger.error(f"[LOGIN ERROR]: invalid email has been entered -> {email}")
        return jsonify(success=False, message="Could not find user with this email, please check inputs and try again"), 401
    
    if not bcrypt.check_password_hash(user.password_hash, pw):
        current_app.logger.error(f"[LOGIN ERROR]: Invalid password has been entered for {email}")
        return jsonify(success=False, message="Invalid credentials"), 401
    
    login_user(user)
    current_app.logger.info(f"{user.first_name} {user.last_name} has logged in.")
    return jsonify(success=True, message=f"Logged in as {user.first_name}", user=user.serialize()), 200


@authorizer.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return jsonify(success=True, message="Logged out."), 200


@authorizer.route('/hydrate_user', methods=['GET'])
@login_required
def hydrate_user():
    user_data = current_user.serialize()
    return jsonify(success=True, user=user_data), 200
