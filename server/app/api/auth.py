from flask import Blueprint, jsonify, request, current_app
from app.models import User, Ticket, Location, Department
from app.schemas import UserRegistrySchema, UserSchema, UserLoginSchema
from app.extensions import db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from marshmallow import ValidationError

authorizer = Blueprint("auth", __name__)



#-------------
# REGISTER NEW USER
#-------------
@authorizer.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    try:
        validated = UserRegistrySchema().load(data)
    except ValidationError as err:
        return jsonify(success=False, message=err.messages), 422
    
    email = validated["email"].lower()
    first_name = validated["first_name"].strip().title()
    last_name = validated["last_name"].strip().title()
    is_admin = validated.get("is_admin", False)
    
    if db.session.query(User).filter_by(email=email).first():
        return jsonify(success=False, message="Email already in use."), 409
    
    department = db.session.query(Department).filter_by(name=validated["department"]).first()
    if not department:
        return jsonify(success=False, message="Invalid department"), 400
    
    location = db.session.query(Location).filter_by(code=validated["location_code"]).first()
    if not location:
        return jsonify(success=False, message="Invalid location code."), 400
    
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        department_id=department.id,
        location_id=location.id,
        is_admin=is_admin,
        password_hash=bcrypt.generate_password_hash(validated["pw"]).decode("utf-8")
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        current_app.logger.info(f"{new_user.first_name} {new_user.last_name} has been registered to Cerberus")
        return jsonify(success=True, message=f"{new_user.first_name} {new_user.last_name} has been registered!"), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[REGISTRATION ERROR]: {e}")
        return jsonify(success=False, message="There was an error when registering new user."), 500
    
    
#-------------
# LOGIN USER
#-------------
@authorizer.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    try:
        validated = UserLoginSchema().load(data)
    except ValidationError as err:
        return jsonify(success=False, message=err.messages), 422
    
    email = validated["email"].lower()
    pw = validated["password"]
    
    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        current_app.logger.error(f"[LOGIN ERROR]: invalid email has been entered -> {email}")
        return jsonify(success=False, message="Could not find user with this email, please check inputs and try again"), 401
    
    if user.terminated:
        return jsonify(success=False, message="User account is terminated"), 403
    
    if not bcrypt.check_password_hash(user.password_hash, pw):
        current_app.logger.error(f"[LOGIN ERROR]: Invalid password has been entered for {email}")
        return jsonify(success=False, message="Invalid credentials"), 401
    
    login_user(user)
    current_app.logger.info(f"{user.first_name} {user.last_name} has logged in.")
    
    user_data = UserSchema().dump(user)
    return jsonify(success=True, message=f"Welcome {user.first_name}", user=user_data), 200

#-------------
# LOGOUT USER
#-------------
@authorizer.route("/logout", methods=["GET"])
@login_required
def logout():
    current_app.logger.info(f"Logging out {current_user.first_name}")
    logout_user()
    return jsonify(success=True, message="Logged out."), 200

#-------------
# HYDRATE USER
#-------------
@authorizer.route('/hydrate_user', methods=['GET'])
@login_required
def hydrate_user():
    user_data = UserSchema().dump(current_user)
    return jsonify(success=True, user=user_data), 200