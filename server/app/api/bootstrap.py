from flask import Blueprint, request, jsonify
from app.models import User, Location
from app.extensions import db, bcrypt

bootstrapper = Blueprint("bootstrap", __name__)

@bootstrapper.route("/status", methods=["GET"])
def bootstrap_status():
    bootstrapped = (
        db.session.query(User).first() is not None
        and db.session.query(Location).first() is not None        
    )
    
    return jsonify(bootstrapped=bootstrapped), 200

# @bootstrapper.route("", methods=["POST"])
# def run_bootstrap():
#     # HARD STOP if already bootstrapped
#     existing_user = db.session.query(User).first()
#     existing_location = db.session.query(Location).first()
    
#     if existing_user or existing_location:
#         return jsonify(success=False, message="System already bootstrapped"), 403
    
#     data = request.get_json()
    
#     #validate inputs
#     if not data or "admin" not in data or "location" not in data:
#         return jsonify(success=False, message="Invalid bootstrap payload"), 400
    
#     location = Location(
#         name=str(data["location"]["name"]).title(),
#         code=str(data["location"]["code"]).lower(),
#     )
    
#     try:
#         department = DepartmentEnum(data["admin"]["department"])
#     except ValueError:
#         return jsonify(success=False, message="Invalid department"), 400
    
#     admin = User(
#         email=data["admin"]["email"],
#         first_name=str(data["admin"]["first_name"]).title(),
#         last_name=str(data["admin"]["last_name"]).title(),
#         department=department,
#         is_admin=True,
#         location=location,
#         password_hash=bcrypt.generate_password_hash(data["admin"]["password"]).decode("utf-8")
#     )
    
#     db.session.add_all([location, admin])
#     db.session.commit()
    
#     return jsonify(success=True, bootstrapped=True, message="Bootstrpping complete!"), 201