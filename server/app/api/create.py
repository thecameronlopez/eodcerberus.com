from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import (
    User, 
    Ticket, 
    Transaction, 
    Tender, 
    LineItem, 
    LineItemTender, 
    Location, 
    TaxRate, 
    Deduction,
    Department,
    PaymentType,
    SalesCategory, 
    SalesDay
)

from app.schemas import (
    LineItemSchema, 
    LineItemTenderSchema, 
    UserSchema, 
    TransactionSchema,
    LocationSchema,
    TenderSchema,
    TicketSchema,
    CreateLi, 
    CreateTicket,
    CreateTender,
    CreateDeduction,
    CreateLocation,
    CreatePaymentType,
    CreateSalesCategory,
    SalesDaySchema,
    CreateTransaction
)
from datetime import datetime, date as DTdate
from marshmallow import Schema, fields, validate, ValidationError
from app.utils.tools import to_int, finalize_ticket, finalize_transaction
from app.utils.constants import PAYMENT_TYPES, SALES_CATEGORIES
from sqlalchemy import select
from app.services.allocations import allocate_tender_to_line_items

creator = Blueprint("create", __name__)



@creator.route("/location", methods=["POST"])
@login_required
def create_location():
    schema = CreateLocation()
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify(success=False, errors=e.messages), 400

    existing = db.session.query(Location).filter(
        (Location.name == data["name"].title()) | 
        (Location.code == data["code"].lower())
    ).first()
    if existing:
        return jsonify(success=False, message="Location already exists"), 409

    new_location = Location(
        name=data["name"].title(),
        code=data["code"].strip().lower(),
        address=data["address"],
        current_tax_rate=data["current_tax_rate"]
    )

    initial_tax = TaxRate(
        location=new_location,
        rate=data["current_tax_rate"],
        effective_from=DTdate.today()
    )

    try:
        db.session.add_all([new_location, initial_tax])
        db.session.commit()
        return jsonify(success=True, new_location=LocationSchema().dump(new_location)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message="Error adding location"), 500




@creator.route("/sales_category", methods=["POST"])
@login_required
def create_sales_category():
    schema = CreateSalesCategory()
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify(success=False, errors=e.messages), 400

    if data["name"].upper() in SALES_CATEGORIES:
        return jsonify(success=False, message="Category already exists"), 409

    SALES_CATEGORIES.append(data["name"].upper())
    return jsonify(success=True, message=f"Category {data['name']} added"), 201






@creator.route("/payment_type", methods=["POST"])
@login_required
def create_payment_type():
    schema = CreatePaymentType()
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify(success=False, errors=e.messages), 400

    if data["name"].upper() in PAYMENT_TYPES:
        return jsonify(success=False, message="Payment type already exists"), 409

    PAYMENT_TYPES.append(data["name"].upper())
    return jsonify(success=True, message=f"Payment type {data['name']} added"), 201




# -------------------------------
# CREATE A NEW TICKET
# -------------------------------
@creator.route("/ticket", methods=["POST"])
@login_required
def create_ticket():
    """
    JSON Payload Example:
    {
        "ticket_number": 1234,
        "date": "2026-01-29",
        "location_id": 1,
        "line_items": [
            {
                "category": 2,
                "unit_price": 50000,
                "quantity": 1,
                "taxable": true,
                "is_return": false
            }
        ],
        "tenders": [
            {
                "payment_type": 1,
                "amount": 50000
            }
        ]
    }
    """
    schema = CreateTicket()
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify(success=False, errors=e.messages), 400

    # Check duplicate ticket_number
    if db.session.query(Ticket).filter_by(ticket_number=data["ticket_number"]).first():
        return jsonify(success=False, message="Ticket number already exists"), 400

    # Fetch location
    location = db.session.get(Location, data["location_id"])
    if not location:
        return jsonify(success=False, message="Invalid location"), 404

    # Fetch user (default to current_user)
    user = current_user

    # Determine or create SalesDay for this user/location/date
    ticket_date = data["date"]
    sales_day = (
        db.session.query(SalesDay)
        .filter_by(user_id=user.id, location_id=location.id, opened_at=ticket_date)
        .first()
    )
    if not sales_day:
        sales_day = SalesDay(
            user_id=user.id,
            location_id=location.id,
            opened_at=ticket_date
        )
        db.session.add(sales_day)
        db.session.flush()  # Assign ID for relationship

    # Create ticket
    ticket = Ticket(
        ticket_number=data["ticket_number"],
        ticket_date=ticket_date,
        location=location,
        user=user,
        sales_day=sales_day
    )

    # Create transaction
    transaction = Transaction(user=user, location=location, posted_date=ticket_date)

    # ------------------- Line Items -------------------
    for li_data in data["line_items"]:
        line_item = LineItem(
            category_id=li_data["category"],
            unit_price=li_data["unit_price"],
            quantity=li_data.get("quantity", 1),
            taxable=li_data.get("taxable", True),
            is_return=li_data.get("is_return", False),
            tax_rate=location.current_tax_rate or 0
        )
        line_item.compute_total()
        transaction.line_items.append(line_item)

    # Compute transaction totals
    transaction.compute_totals()
    ticket.transactions.append(transaction)

    # ------------------- Tenders -------------------
    tenders_data = data.get("tenders")
    if not tenders_data:
        # Default tender: cash full amount
        tenders_data = [{"payment_type": 1, "amount": transaction.total}]

    for t_data in tenders_data:
        tender = Tender(payment_type=t_data["payment_type"], amount=t_data["amount"])
        transaction.tenders.append(tender)
        allocations = allocate_tender_to_line_items(transaction, tender)
        db.session.add_all(allocations)

    # Finalize ticket
    finalize_ticket(ticket)

    try:
        db.session.add(ticket)
        db.session.commit()
        return jsonify(success=True, ticket=ticket.serialize(include_relationships=True)), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[CREATE TICKET ERROR]: {e}")
        return jsonify(success=False, message="Error creating ticket"), 500


# -------------------------------
# ADD A TRANSACTION TO EXISTING TICKET
# -------------------------------
@creator.route("/transaction/<int:ticket_id>", methods=["POST"])
@login_required
def create_transaction(ticket_id):
    """
    JSON Payload Example:
    {
        "posted_date": "2026-01-29",
        "location_id": 1,
        "line_items": [
            {
                "category": 2,
                "unit_price": 25000,
                "quantity": 1,
                "taxable": true,
                "is_return": false
            }
        ],
        "tenders": [
            {
                "payment_type": 1,
                "amount": 25000
            }
        ]
    }
    """
    schema = CreateTransaction()
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify(success=False, errors=e.messages), 400

    # Fetch ticket
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify(success=False, message="Ticket not found"), 404

    # Fetch location
    location = db.session.get(Location, data["location_id"])
    if not location:
        return jsonify(success=False, message="Invalid location"), 404

    user = current_user

    # Determine or create SalesDay
    posted_date = data["posted_date"]
    sales_day = (
        db.session.query(SalesDay)
        .filter_by(user_id=user.id, location_id=location.id, opened_at=posted_date)
        .first()
    )
    if not sales_day:
        sales_day = SalesDay(user_id=user.id, location_id=location.id, opened_at=posted_date)
        db.session.add(sales_day)
        db.session.flush()

    # Create transaction
    transaction = Transaction(user=user, location=location, posted_date=posted_date)

    for li_data in data["line_items"]:
        line_item = LineItem(
            category_id=li_data["category"],
            unit_price=li_data["unit_price"],
            quantity=li_data.get("quantity", 1),
            taxable=li_data.get("taxable", True),
            is_return=li_data.get("is_return", False),
            tax_rate=location.current_tax_rate or 0
        )
        line_item.compute_total()
        transaction.line_items.append(line_item)

    transaction.compute_totals()
    ticket.transactions.append(transaction)

    # Tenders
    tenders_data = data.get("tenders")
    if not tenders_data:
        tenders_data = [{"payment_type": 1, "amount": transaction.total}]

    for t_data in tenders_data:
        tender = Tender(payment_type=t_data["payment_type"], amount=t_data["amount"])
        transaction.tenders.append(tender)
        allocations = allocate_tender_to_line_items(transaction, tender)
        db.session.add_all(allocations)

    # Finalize transaction
    finalize_transaction(transaction)
    ticket.compute_total()

    try:
        db.session.add(transaction)
        db.session.commit()
        return jsonify(success=True, ticket=ticket.serialize(include_relationships=True)), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[CREATE TRANSACTION ERROR]: {e}")
        return jsonify(success=False, message="Error creating transaction"), 500




# app/api/create.py

@creator.route("/deduction", methods=["POST"])
@login_required
def create_deduction():
    """
    JSON Payload Example:
    {
        "user_id": 1,          # optional, defaults to current_user if omitted
        "amount": 2500,
        "reason": "Returned item",
        "date": "2026-01-29",
        "location_id": 1       # required
    }
    """
    schema = CreateDeduction()
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify(success=False, errors=e.messages), 400

    # Use current_user if user_id is not provided
    user = db.session.get(User, data.get("user_id", current_user.id))
    if not user:
        return jsonify(success=False, message="Invalid user"), 404

    # Fetch location
    location = db.session.get(Location, data["location_id"])
    if not location:
        return jsonify(success=False, message="Invalid location"), 404

    deduction_date = data["date"]

    # Determine or create SalesDay for this deduction
    sales_day = (
        db.session.query(SalesDay)
        .filter_by(user_id=user.id, location_id=location.id, opened_at=deduction_date)
        .first()
    )
    if not sales_day:
        sales_day = SalesDay(
            user_id=user.id,
            location_id=location.id,
            opened_at=deduction_date
        )
        db.session.add(sales_day)
        db.session.flush()  # Assign ID

    # Create deduction
    deduction = Deduction(
        user=user,
        amount=data["amount"],
        reason=data["reason"],
        date=deduction_date,
        sales_day_id=sales_day.id
    )

    try:
        db.session.add(deduction)
        db.session.commit()
        return jsonify(success=True, deduction=deduction.serialize()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[CREATE DEDUCTION ERROR]: {e}")
        return jsonify(success=False, message="Error creating deduction"), 500

