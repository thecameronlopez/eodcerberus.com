from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models import Ticket, LineItem, Transaction, Deduction, User, Location, Department, PaymentType, SalesCategory
from app.schemas import UserSchema, LocationSchema, PaymentType, SalesCategorySchema, DepartmentSchema
from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import selectinload

reader = Blueprint("reader", __name__)


@reader.route("/users", methods=["GET"])
@login_required
def get_users():
    users = db.session.query(User).all()
    return jsonify(success=True, users=[UserSchema().dump(u) for u in users]), 200

@reader.route("/locations", methods=["GET"])
@login_required
def get_locations():
    locations = db.session.query(Location).all()
    return jsonify(success=True, locations=[LocationSchema().dump(l) for l in locations]), 200


@reader.route("/departments", methods=["GET"])
@login_required
def get_departments():
    departments = db.session.query(Department).all()
    return jsonify(success=True, users=[DepartmentSchema().dump(d) for d in departments]), 200

@reader.route("/categories", methods=["GET"])
@login_required
def get_categories():
    categories = db.session.query(SalesCategory).all()
    return jsonify(success=True, locations=[SalesCategorySchema().dump(c) for c in categories]), 200

@reader.route("/payment_types", methods=["GET"])
@login_required
def get_payment_types():
    payment_types = db.session.query(PaymentType).all()
    return jsonify(success=True, locations=[LocationSchema().dump(p) for p in payment_types]), 200