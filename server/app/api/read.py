from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models import Ticket, LineItem, Transaction, Deduction, User, Location, Department, PaymentType, SalesCategory
from app.schemas import (
    user_schema,
    location_schema,
    payment_type_schema,
    ticket_schema,
    sales_category_schema,
    department_schema,
    deduction_schema,
    line_item_schema, 
    line_item_tender_schema,
    sales_day_schema,
    transaction_schema,
    taxrate_schema,
    tender_schema,
    many_deductions_shema,
    many_departments_schema, 
    many_line_item_tenders_schema, 
    many_line_items_schema, 
    many_locations_schema, 
    many_payment_types_schema, 
    many_sales_categories_schema, 
    many_sales_days_schema, 
    many_taxrates_schema, 
    many_tenders_schema, 
    many_tickets_schema, 
    many_transactions_schema, 
    many_users_schema
)
from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import selectinload

reader = Blueprint("reader", __name__)

#----------------------------------------
#----------------------------------------
#   READ ALL USERS
#----------------------------------------
#----------------------------------------
@reader.route("/users", methods=["GET"])
@login_required
def get_users():
    users = db.session.query(User).all()
    return jsonify(success=True, users=many_users_schema.dump(users)), 200



#----------------------------------------
#----------------------------------------
#   READ ALL LOCATIONS
#----------------------------------------
#----------------------------------------
@reader.route("/locations", methods=["GET"])
@login_required
def get_locations():
    locations = db.session.query(Location).all()
    return jsonify(success=True, locations=many_locations_schema.dump(locations)), 200



#----------------------------------------
#----------------------------------------
#   READ ALL DEPARTMENTS
#----------------------------------------
#----------------------------------------
@reader.route("/departments", methods=["GET"])
@login_required
def get_departments():
    departments = db.session.query(Department).all()
    return jsonify(success=True, departments=many_departments_schema.dump(departments)), 200



#----------------------------------------
#----------------------------------------
#   READ ALL CATEGORIES
#----------------------------------------
#----------------------------------------
@reader.route("/sales_categories", methods=["GET"])
@login_required
def get_sles_categories():
    sales_categories = db.session.query(SalesCategory).all()
    return jsonify(success=True, sales_categories=many_sales_categories_schema.dump(sales_categories)), 200


#----------------------------------------
#----------------------------------------
#   READ ALL PAYMENT TYPES
#----------------------------------------
#----------------------------------------
@reader.route("/payment_types", methods=["GET"])
@login_required
def get_payment_types():
    payment_types = db.session.query(PaymentType).all()
    return jsonify(success=True, payment_types=many_payment_types_schema.dump(payment_types)), 200


#----------------------------------------
#----------------------------------------
#   READ ALL TICKETS
#----------------------------------------
#----------------------------------------
@reader.route("/tickets", methods=["GET"])
@login_required
def get_tickets():
    tickets = db.session.query(Ticket).all()
    return jsonify(success=True, tickets=many_tickets_schema.dump(tickets)), 200