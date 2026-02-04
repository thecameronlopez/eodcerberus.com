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
    create_line_item_schema,
    create_ticket_schema,
    create_sales_day_schema,
    close_sales_day_schema,
    create_tender_schema,
    create_line_item_tender_schema,
    create_location_schema,
    create_taxrate_schema,
    create_deduction_schema,
    create_department_schema,
    create_payment_type_schema,
    create_sales_category_schema,
    create_transaction_schema,
    
    line_item_schema,
    ticket_schema,
    sales_day_schema,
    tender_schema,
    line_item_tender_schema,
    location_schema,
    taxrate_schema,
    deduction_schema,
    department_schema,
    payment_type_schema,
    sales_category_schema,
    transaction_schema,
    
    many_line_items_schema,
    many_tickets_schema,
    many_sales_days_schema,
    many_tenders_schema,
    many_line_item_tenders_schema,
    many_locations_schema,
    many_taxrates_schema,
    many_deductions_shema,
    many_departments_schema,
    many_payment_types_schema,
    many_sales_categories_schema,
    many_transactions_schema,
    many_users_schema,
    
    user_schema
)


from datetime import datetime, date as DTdate
from marshmallow import Schema, fields, validate, ValidationError
from app.utils.tools import to_int, finalize_ticket, finalize_transaction
from app.utils.constants import PAYMENT_TYPES, SALES_CATEGORIES
from sqlalchemy import select
from app.services.allocations import allocate_tender_to_line_items

creator = Blueprint("create", __name__)

#----------------------------------------
#----------------------------------------
#   CREATE A NEW LOCATION
#----------------------------------------
#----------------------------------------
@creator.route("/location", methods=["POST"])
@login_required
def create_location():
    try:
        data = create_location_schema.load(request.get_json())
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
        return jsonify(success=True, new_location=location_schema.dump(new_location)), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[NEW LOCATION ERROR]: {e}")
        return jsonify(success=False, message="Error adding location"), 500



#----------------------------------------
#----------------------------------------
#   CREATE A NEW SALES CATEGORY
#----------------------------------------
#----------------------------------------
@creator.route("/sales_category", methods=["POST"])
@login_required
def create_sales_category():
    try:
        data = create_sales_category_schema.load(request.get_json())
    except ValidationError as e:
        print(e)
        return jsonify(success=False, errors=e.messages), 400

    if db.session.query(SalesCategory).filter_by(name=data["name"].title()).first():
        return jsonify(success=False, message="Category already exists"), 409

    new_category = SalesCategory(
        name=data["name"].title(),
        taxable=data.get("taxable", True),
        active=True
    )
    
    try:
        db.session.add(new_category)
        db.session.commit()
        current_app.logger.info(f"[NEW CATEGORY]: {new_category.name} added to database")
        return jsonify(success=True, message=f"Category {data['name']} added", new_category=sales_category_schema.dump(new_category)), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[NEW CATEGORY ERROR]: {e}")
        return jsonify(success=False, message="There was an error when adding new sales category"), 500


#----------------------------------------
#----------------------------------------
#   CREATE A NEW PAYMENT TYPE
#----------------------------------------
#----------------------------------------
@creator.route("/payment_type", methods=["POST"])
@login_required
def create_payment_type():
    try:
        data = create_payment_type_schema.load(request.get_json())
    except ValidationError as e:
        print(e)
        return jsonify(success=False, errors=e.messages), 400

    if db.session.query(PaymentType).filter_by(name=data["name"].title()).first():
        return jsonify(success=False, message="Payment type already exists"), 409

    new_payment_type = PaymentType(
        name=data["name"].title(),
        taxable=data["taxable"],
        active=True
    )
    
    try:
        db.session.add(new_payment_type)
        db.session.commit()
        current_app.logger.info(f"New payment type {new_payment_type.name} added to database")
        return jsonify(success=True, message=f"Payment type {new_payment_type.name} added", new_payment_type=payment_type_schema.dump(new_payment_type)), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[NEW PAYMENT TYPE ERROR]: {e}")
        return jsonify(success=False, message="There was an error when adding a new payment type"), 500


#----------------------------------------
#----------------------------------------
#   CREATE A NEW DEPARTMENT
#----------------------------------------
#----------------------------------------
@creator.route("/department", methods=["POST"])
@login_required
def create_department():
    try:
        data = create_department_schema.load(request.get_json())
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
        return jsonify(success=True, message="New department added!", new_department=department_schema.dump(new_department)), 201
    except Exception as e:
        current_app.logger.error(f"[NEW DEPARTMENT ERROR]: {e}")
        return jsonify(success=False, message="There was an error when adding a new department"), 500
    

#----------------------------------------
#----------------------------------------
#   CREATE A NEW DEDUCTION
#----------------------------------------
#----------------------------------------
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
    try:
        data = create_deduction_schema.load(request.get_json())
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
        return jsonify(success=True, deduction=deduction_schema.dump(deduction)), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[CREATE DEDUCTION ERROR]: {e}")
        return jsonify(success=False, message="Error creating deduction"), 500




#----------------------------------------
#----------------------------------------
#   CREATE A NEW TICKET
#----------------------------------------
#----------------------------------------
@creator.route("/ticket", methods=["POST"])
@login_required
def create_ticket():
    """  
    JSON PAYLOAD EXAMPLE:
    {
        ticket_number: 1234, -> int
        date: 2026-01-01, -> str
        user_id: 1, -> int
        location_id: 1, -> int
        transaction_type: SALE, -> enum str
        line_items: [
            {
                sales_category_id: 1, -> int
                unit_price: 50000, -> int
                quantity: 1, -> int                
            }, -> dict
        ], -> list
        tenders: [
            {
                amount: 50000, -> int
                payment_type_id: 1, -> int    
            }, -> dict    
        ], -> list
    }
    """
    try:
        data = create_ticket_schema.load(request.get_json())
    except ValidationError as e:
        print(f"[TICKET VALIDATION ERROR]: {e}")
        return jsonify(success=False, message=e.messages), 400
    
    #---------- Initialize meta data ------------
    user = db.session.get(User, data["user_id"])
    if not user:
        return jsonify(success=False, message="User not found."), 404
    
    location = db.session.get(Location, data["location_id"])
    if not location:
        return jsonify(success=False, message="Location not found"), 404
    
    #-------------- format date -----------------
    date = data["date"]
    
    
    #-------------- create sales day if not one --------------
    existing_sales_day = db.session.query(SalesDay).filter_by(user_id=user.id).first()
    if existing_sales_day:
        sales_day = existing_sales_day
    else:
        sales_day = SalesDay(
            user_id=user.id,
            location_id=location.id,
            opened_at=datetime.today(),
        )
        
    existing_ticket = db.session.query(Ticket).filter_by(ticket_number=data["ticket_number"]).first()
    if existing_ticket:
        return jsonify(success=False, message=f"Ticket number {existing_ticket.ticket_number} already used"), 409
    ticket = Ticket(
        ticket_number=data["ticket_number"],
        ticket_date=date,
        location_id=location.id,
        user_id=user.id
    )
    sales_day.tickets.append(ticket)
        
    transaction = Transaction(
        ticket_id=ticket.id,
        user_id=user.id,
        location_id=location.id,
        posted_at=date,
        transaction_type=data["transaction_type"]
    )
    ticket.transactions.append(transaction)
    
    line_items = []
    for li in data["line_items"]:
        sales_category = db.session.get(SalesCategory, li["sales_category_id"])
        line_item = LineItem(
            sales_category_id=sales_category.id,
            unit_price=li["unit_price"],
            quantity=li["quantity"],
            taxable=sales_category.taxable,
            taxability_source="CATEGORY_DEFAULT",
            tax_rate=location.current_tax_rate
        )
        line_items.append(line_item)
        transaction.line_items.append(line_item)
        
    tenders = []
    for t in data["tenders"]:
        payment_type = db.session.get(PaymentType, t["payment_type_id"])
        tender = Tender(
            payment_type_id=payment_type.id,
            amount=t["amount"]
        )
        tenders.append(tender)
        transaction.tenders.append(tender)
        
    for t in tenders:
        allocations = allocate_tender_to_line_items(transaction, t)
        t.allocations.extend(allocations)
    
    finalize_ticket(ticket)
    
    try:
        db.session.add(sales_day)
        db.session.commit()
        current_app.logger.info(f"[NEW TICKET CREATED]: {user.first_name} {user.last_name} created a new ticket: {ticket.ticket_number}")
        return jsonify(
            success=True,
            message="Ticket created successfully!",
            ticket=ticket_schema.dump(ticket)
        ), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[TICKET SUBMISSION ERROR]: {e}")
        return jsonify(success=False, message="There was an error when creating a new ticket."), 500
    


#----------------------------------------
#----------------------------------------
#   CREATE A NEW TRANSACTION ON EXITING TICKET
#----------------------------------------
#----------------------------------------