from flask import Blueprint, request, jsonify
from app.models import User, Location, Department
from app.extensions import db, bcrypt
from app.schemas import UserRegistrySchema, LocationSchema, CreateLocation, CreateDepartment
from marshmallow import ValidationError, fields, validate

bootstrapper = Blueprint("bootstrap", __name__)

@bootstrapper.route("/status", methods=["GET"])
def bootstrap_status():
    bootstrapped = (
        db.session.query(User).first() is not None
        and db.session.query(Location).first() is not None        
    )
    
    return jsonify(bootstrapped=bootstrapped), 200

@bootstrapper.route("", methods=["POST"])
def run_bootstrap():
    """   
    JSON PAYLOAD
    {
        "location": {
            "name": "Lake Charles",
            "code": "lake_charles",
            "address": "2600 Common St.",
            "current_tax_rate": 0.1075,
        }
        "admin": {
            "first_name": "Cameron",
            "last_name": "Lopez",
            "email": "cameron@mattsappliancesla.net",
            "pw": "password",
            "pw2": "password",
            "is_admin": "true",
        },
        "department": {
            "name": "office"
        }
    }
    """
    # HARD STOP if already bootstrapped
    existing_user = db.session.query(User).first()
    existing_location = db.session.query(Location).first()
    
    if existing_user or existing_location:
        return jsonify(success=False, message="System already bootstrapped"), 403
    
    data = request.get_json()
    print(data)
    #validate inputs
    if not data or "admin" not in data or "location" not in data:
        return jsonify(success=False, message="Invalid bootstrap payload"), 400
    try:
        location_data = CreateLocation().load(data["location"])
        user_data = UserRegistrySchema().load(data["admin"])
        deaprtment_data = CreateDepartment().load(data["department"])
    except ValidationError as err:
        print(err.messages)
        return jsonify(success=False, message=f"There was an error: {err.messages}"), 400
    
    location = Location(
        name=location_data["name"].title(),
        code=location_data["code"].lower(),
    )
    db.session.flush()
    
    department = Department(
        name=deaprtment_data["name"],
        active=True
    )
    db.session.flush()
    
    
    admin = User(
        email=user_data["email"].lower(),
        first_name=user_data["first_name"].title(),
        last_name=user_data["last_name"].title(),
        department=department,
        is_admin=user_data.get("is_admin", True),
        location=location,
        password_hash=bcrypt.generate_password_hash(user_data["pw"]).decode("utf-8")
    )
    
    db.session.add_all([location, admin])
    db.session.commit()
    
    return jsonify(success=True, bootstrapped=True, message="Bootstrpping complete!"), 201