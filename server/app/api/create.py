from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models import User, Ticket, Transaction, LineItem, Location, TaxRate, Deduction, SalesCategoryEnum, TaxabilitySourceEnum, PaymentTypeEnum
from app.models.services.tax_rules import determine_taxability
from app.extensions import db
from datetime import datetime, date as DTdate
from app.utils.tools import to_int, to_cents, finalize_ticket, finalize_transaction
from sqlalchemy import select

creator = Blueprint("create", __name__)

# ----------------------------
# Create a new location
# ----------------------------
@creator.route("/location", methods=["POST"])
@login_required
def create_location():
    data = request.get_json()
    
    name = data.get("name")
    code = data.get("code")
    address = data.get("address")
    current_tax_rate = data.get("current_tax_rate")
    
    if current_tax_rate is not None:
        try:
            current_tax_rate = float(current_tax_rate)
            if current_tax_rate < 0 or current_tax_rate > 1:
                raise ValueError
        except ValueError:
            return jsonify(success=False, message="Invalid tax rate"), 400
    else:
        current_tax_rate = 0.0
    
    existing = db.session.query(Location).filter(
        (Location.name == name.title()) |
        (Location.code == code.lower())
    ).first()
    
    if existing:
        return jsonify(success=False, message="Location already exists"), 409
    
    new_location = Location(
        name=name.title(),
        code=code.strip().lower(),
        address=address,
        current_tax_rate=current_tax_rate
    )
    
    initial_tax = TaxRate(
        location=new_location,
        rate=current_tax_rate,
        effective_from=DTdate.today(),
        effective_to=None
    )
    
    try:
        db.session.add_all([new_location, initial_tax])
        db.session.commit()
        current_app.logger.info(f"[NEW LOCATION ADDED]: {current_user.first_name} {current_user.last_name} added a new location: {name} | tax rate: {current_tax_rate}")
        return jsonify(success=True, message=f"New location {name}, has been added", new_location=new_location.serialize()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[NEW LOCATION ERROR]: {e}")
        return jsonify(success=False, message="Error when adding new location"), 500
    

# ----------------------------
# Create a new ticket
# ----------------------------
@creator.route("/ticket", methods=["POST"])
@login_required
def create_ticket():
    #Payload example from react
    # {
    #     "ticket_number": 12345,
    #     "date": "2026-01-01",
    #     "location_id": 1,
    #     "user_id": 1,
    #     "line_items": [
    #             {
    #                 "category": "NEW_APPLIANCE",
    #                 "payment_type": CARD,
    #                 "unit_price": 50000,
    #                 "is_return": False
    #             }
    #         ]
    # }
    data = request.get_json()
    existing = db.session.query(Ticket).filter_by(ticket_number=data.get("ticket_number")).first()
    if existing:
        return jsonify(success=False, message=f"Ticket Number {existing.ticket_number} already in use."), 400
    
    # -------------------
    # Parse ticket date
    # -------------------
    ticket_date = datetime.strptime(
        data.get("date", datetime.today().isoformat()), "%Y-%m-%d"
    ).date()

    # -------------------
    # Fetch location
    # -------------------
    location = db.session.get(Location, int(data["location_id"]))
    if not location:
        return jsonify(success=False, message="Invalid location"), 404

    # -------------------
    # Fetch user
    # -------------------
    user = db.session.get(User, int(data["user_id"]))
    if not user:
        return jsonify(success=False, message="User not found"), 404

    # -------------------
    # Create ticket
    # -------------------
    ticket = Ticket(
        ticket_number=data["ticket_number"],
        ticket_date=ticket_date,
        location=location,
        user=user
    )

    # -------------------
    # Create transaction
    # -------------------
    transaction = Transaction(
        user=user,
        location=location,
        posted_date=ticket_date
    )

    # -------------------
    # Create line items and attach
    # -------------------
    for li_data in data.get("line_items", []):
        try:
            category = SalesCategoryEnum(li_data["category"])
            payment_type = PaymentTypeEnum(li_data["payment_type"])
        except ValueError:
            return jsonify(success=False, message="Invalid sales category or payment type"), 400

        taxable, tax_source = determine_taxability(
            category=category,
            payment_type=payment_type,
            location=location
        )

        line_item = LineItem(
            category=category,
            payment_type=payment_type,
            unit_price=to_int(li_data["unit_price"]),
            taxable=taxable,
            taxability_source=tax_source,
            tax_rate=location.current_tax_rate or 0,
            is_return=bool(li_data.get("is_return", False))
        )

        # Attach line item to transaction
        transaction.line_items.append(line_item)

    # Attach transaction to ticket
    ticket.transactions.append(transaction)

    # -------------------
    # Commit to DB
    # -------------------
    try:
        db.session.add(ticket)
        finalize_ticket(ticket)
        db.session.commit()
        current_app.logger.info(
            f"[NEW TICKET]: {user.first_name} {user.last_name} added ticket #{ticket.ticket_number}"
        )
        return jsonify(
            success=True,
            message="Ticket added successfully!",
            ticket=ticket.serialize(include_relationships=True)
        ), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[NEW TICKET ERROR]: {e}")
        return jsonify(success=False, message="There was an error when submitting ticket"), 500



# ----------------------------
# Add a new transaction to an existing ticket
# ----------------------------
@creator.route("/transaction/<int:ticket_id>", methods=["POST"])
@login_required
def add_transaction(ticket_id):
    """
    payload example:
    
    {
        "posted_date": "2026-01-01",
        "location_id": 2,
        "user_id": 1,
        "line_items": [
            {
                "category": "USED_APPLIANCE",
                "payment_type": CARD,
                "unit_price": 25000,
                "is_return": False,
            }
        ]
    }
    
    """
    data = request.get_json()
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify(success=False, message="Ticket not found"), 404
    location = db.session.get(Location, int(data["location_id"]))
    if not location:
        return jsonify(success=False, message="Invalid location"), 404
    user = db.session.get(User, int(data["user_id"]))
    if not user:
        return jsonify(success=False, message="User not found"), 404
    
    posted_date = datetime.strptime(data.get("posted_date", datetime.today().isoformat()), "%Y-%m-%d").date()
    
    #---------------
    # Create transaction
    #---------------
    transaction = Transaction(
        user=user,
        location=location,
        posted_date=posted_date
    )
    
    ticket.transactions.append(transaction)
    
    #---------------
    # Create line items
    #---------------
    for li in data.get("line_items", []):
        try:
            category = SalesCategoryEnum(li["category"])
            payment_type = PaymentTypeEnum(li["payment_type"])
        except ValueError:
            return jsonify(success=False, message="Invalid sales category")
        
        taxable, tax_source = determine_taxability(
            category=category,
            payment_type=payment_type,
            location=location
        )
        
        line_item = LineItem(
            category=category,
            payment_type=payment_type,
            unit_price=to_cents(li["unit_price"]),
            taxable=taxable,
            taxability_source=tax_source,
            tax_rate=location.current_tax_rate or 0,
            is_return=li.get("is_return", False)
        )
        # append line items to transaction
        transaction.line_items.append(line_item)
            
    try:
        db.session.add(transaction)
        finalize_transaction(transaction)
        ticket.compute_total()
        db.session.commit()
        return jsonify(
            success=True,
            message="Transaction added successfully",
            ticket=ticket.serialize(include_relationships=True)
        ), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[ADD TRANSACTION ERROR]: {e}")
        return jsonify(success=False, message="Error adding transaction"), 500


# ----------------------------
# Create a deduction for a user
# ----------------------------
@creator.route("/deduction", methods=["POST"])
@login_required
def create_deduction():
    data = request.get_json()
    
    amount = data.get("amount")
    reason = data.get("reason")
    date_obj = datetime.strptime(data.get("date"), "%Y-%m-%d").date() if data.get("date") else datetime.today().date()
    
    if not amount or not reason:
        return jsonify(success=False, message="Amount and reason are required"), 400
    
    if to_int(amount) <= 0:
        return jsonify(success=False, message="Amount must be greater than 0"), 400
    
    deduction = Deduction(
        user_id=current_user.id,
        amount=to_int(amount),
        reason=reason,
        date=date_obj
    )
    
    try:
        db.session.add(deduction)
        db.session.commit()
        current_app.logger.info(f"[DEDUCTION CREATED]: {current_user.first_name} {current_user.last_name} created deduction {deduction.id}")
        return jsonify(success=True, message="Deduction submitted!", deduction=deduction.serialize()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[DEDUCTION CREATION ERROR]: {e}")
        return jsonify(success=False, message="Error submitting deduction."), 500
