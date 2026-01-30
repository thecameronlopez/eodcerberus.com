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
    PaymentTypeSchema,
    CreateSalesCategory,
    SalesCategorySchema,
    SalesDaySchema,
    CreateTransaction,
    CreateDepartment,
    DepartmentSchema
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
        print(e)
        return jsonify(success=False, errors=e.messages), 400

    if db.session.query(SalesCategory).filter_by(name=data["name"].title()).first():
        return jsonify(success=False, message="Category already exists"), 409

    SALES_CATEGORIES.append(data["name"].upper())
    new_category = SalesCategory(
        name=data["name"].title(),
        tax_default=data.get("tax_default", True),
        active=True
    )
    
    try:
        db.session.add(new_category)
        db.session.commit()
        current_app.logger.info(f"[NEW CATEGORY]: {new_category.name} added to database")
        return jsonify(success=True, message=f"Category {data['name']} added", new_category=SalesCategorySchema().dump(new_category)), 201
    except Exception as e:
        current_app.logger.error(f"[NEW CATEGORY ERROR]: {e}")
        return jsonify(success=False, message="There was an error when adding new sales category"), 500



@creator.route("/payment_type", methods=["POST"])
@login_required
def create_payment_type():
    schema = CreatePaymentType()
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        print(e)
        return jsonify(success=False, errors=e.messages), 400

    if db.session.query(PaymentType).filter_by(name=data["name"].title()).first():
        return jsonify(success=False, message="Payment type already exists"), 409

    PAYMENT_TYPES.append(data["name"].upper())
    new_payment_type = PaymentType(
        name=data["name"].title(),
        taxable=data["taxable"],
        active=True
    )
    
    try:
        db.session.add(new_payment_type)
        db.session.commit()
        current_app.logger.info(f"New payment type {new_payment_type.name} added to database")
        return jsonify(success=True, message=f"Payment type {new_payment_type.name} added", new_payment_type=PaymentTypeSchema().dump(new_payment_type)), 201
    except Exception as e:
        current_app.logger.error(f"[NEW PAYMENT TYPE ERROR]: {e}")
        return jsonify(success=False, message="There was an error when adding a new payment type"), 500


@creator.route("/department", methods=["POST"])
@login_required
def create_department():
    schema = CreateDepartment()
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify(success=False, message=e.messages), 400
    
    if db.session.query(Department).filter_by(name=data["name"].title()).first():
        return jsonify(success=False, message=f"This department name already exists: {data['name']}"), 400
    
    new_department = Department(
        name=data["name"].title(),
        active=True
    )
    
    try:
        db.session.add(new_department)
        db.session.commit()
        current_app.logger.info(f"New department '{new_department.name}' has beed added")
        return jsonify(success=True, message="New department added!", new_department=DepartmentSchema().dump(new_department)), 201
    except Exception as e:
        current_app.logger.error(f"[NEW DEPARTMENT ERROR]: {e}")
        return jsonify(success=False, message="There was an error when adding a new department"), 500
    




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
                "category_id": 2,
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
    data = request.get_json()
    ticket_schema = CreateTicket()
    try:
        ticket_data = ticket_schema.load(data)
    except ValidationError as e:
        print(f"[TICKET VALIDATION ERROR]: {e}")
        return jsonify(success=False, errors=e.messages), 400

    # ---------------- Validate duplicates and relations ----------------
    if db.session.query(Ticket).filter_by(ticket_number=ticket_data["ticket_number"]).first():
        print(f"[EXISTING TICKET NUMBER ERROR]: {data['ticket_number']}")
        return jsonify(success=False, message="Ticket number already exists"), 400

    location = db.session.get(Location, ticket_data["location_id"])
    if not location:
        return jsonify(success=False, message="Invalid location"), 404

    user = db.session.get(User, ticket_data["user_id"])
    if not user:
        return jsonify(success=False, message="Invalid user id"), 400

    ticket_date = ticket_data["date"]
    
    # ---------------- SalesDay ----------------
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

    # ---------------- Ticket ----------------
    ticket = Ticket(
        ticket_number=ticket_data["ticket_number"],
        ticket_date=ticket_date,
        location=location,
        user=user,
        sales_day=sales_day
    )
    db.session.add(ticket)

    # ---------------- Transaction ----------------
    transaction = Transaction(user=user, location=location, posted_at=ticket_date, transaction_type="debit")
    ticket.transactions.append(transaction)


    # ------------------- Line Items -------------------
    line_item_schema = CreateLi(many=True)
    try:
        line_item_data = line_item_schema.load(ticket_data.get("line_items", []))
    except ValidationError as e:
        print(f"[LINE ITEM LOAD]: {ticket_data.get('line_items')}")
        print(f"[LINE ITEM VALIDATION ERROR]: {e}")
        return jsonify(success=False, message=e.messages), 400
    
    for li_data in line_item_data:
        line_item = LineItem(
            category_id=li_data["category_id"],
            transaction=transaction,
            unit_price=int(li_data["unit_price"]),
            quantity=li_data.get("quantity", 1),
            taxable=li_data.get("taxable", True),
            is_return=li_data.get("is_return", False),
            tax_rate=location.current_tax_rate or 0,
            taxability_source="PRODUCT_DEFAULT"
        )
        # line_item.compute_total()
        transaction.line_items.append(line_item)
        
    # Compute transaction totals
    transaction.compute_total()

    # ------------------- Tenders -------------------
    tenders_schema = CreateTender(many=True)
    tenders_data = ticket_data.get("tenders", []) or [{"payment_type": 1, "amount": transaction.total}] 
    try:
        tenders_data = tenders_schema.load(tenders_data)
    except ValidationError as e:
        print(f"[TENDER VALIDATIN ERROR]: {e}")
        return jsonify(success=False, message=e.messages), 400
    

    for t_data in tenders_data:
        transaction.tenders.append(Tender(
            payment_type_id=t_data["payment_type"], 
            amount=int(t_data["amount"]), 
            transaction=transaction
        ))
    db.session.flush()
    for tender in transaction.tenders:
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

