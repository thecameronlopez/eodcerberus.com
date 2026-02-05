from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models import Ticket, LineItem, Deduction, User, Location, TaxRate, Transaction, Department
from app.extensions import db
from datetime import datetime, timedelta, date
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.utils.tools import to_int
from app.schemas import (
    location_schema,
    user_schema,
    department_schema,
    line_item_schema,
    deduction_schema,
    payment_type_schema,
    sales_category_schema,
    sales_day_schema,
    ticket_schema,
    transaction_schema,
    line_item_tender_schema,
    tender_schema,
    taxrate_schema,
    update_department_schema
)

updator = Blueprint("update", __name__)


@updator.route("/department/<int:id>", methods=["PATCH"])
@login_required
def update_department(id):
    department = db.session.get(Department, id)
    if not department:
        return jsonify(success=False, message="Invalid department id in url parameter, or, department does not exist."), 404
    data = request.get_json()
    if not data:
        return jsonify(success=False, message="Missing JSON payload"), 404
    try:
        department = update_department_schema.load(data, instance=department, partial=True)
    
        db.session.commit()
        
        return jsonify(success=True, message="Department has been updated", department=department_schema.dump(department)), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[UPDATE DEPARTMENT ERROR]: {e}")
        return jsonify(success=False, message="There was an error when updating department"), 500