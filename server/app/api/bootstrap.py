from flask import Blueprint, request, jsonify
from app.models import User, Location, Department, TaxRate
from app.extensions import db, bcrypt
from app.schemas import (

    user_register_schema,
    location_create_schema,
    department_create_schema,
    taxrate_create_schema
)
from marshmallow import ValidationError, fields, validate
import datetime

bootstrapper = Blueprint("bootstrap", __name__)

boot_data = {
    "user": {
    "first_name": "Cameron",
    "last_name": "Lopez",
    "email": "cameron@mattsappliancesla.net",
    "is_admin": "true",
    "pw": "Claire18!",
    "pw2": "Claire18!"
    },
    "location": {
        "name": "Lake Charles",
        "code": "lake_charles",
        "current_tax_rate": 0.1075
    },
    "department": {
        "name": "Office"
    }
}

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
        "user": {
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
    
    # data = request.get_json()
    # #validate inputs
    # if not data:
    #     data = boot_data
    try:
        location_data = location_create_schema.load(boot_data["location"])
        user_data =user_register_schema.load(boot_data["user"])
        deaprtment_data = department_create_schema.load(boot_data["department"])
    except ValidationError as err:
        print(err.messages)
        return jsonify(success=False, message=f"There was an error: {err}"), 400
    
    
    
    location = Location(
        name=location_data["name"].title(),
        code=location_data["code"].lower(),
        current_tax_rate=location_data["current_tax_rate"]
    )
    db.session.flush()
    
    tax_rate = TaxRate(
        location_id=location.id,
        rate=location.current_tax_rate,
        effective_from=datetime.date.today()
    )
    location.tax_rates.append(tax_rate)
    
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
    
    db.session.add_all([location, admin, department])
    db.session.commit()
    
    return jsonify(success=True, bootstrapped=True, message="Bootstrapping complete!"), 201