from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models import User, Ticket, Transaction, Tender, LineItem, Location, TaxRate, Deduction, SalesCategoryEnum, TaxabilitySourceEnum, PaymentTypeEnum
from app.models.services.tax_rules import determine_taxability
from app.extensions import db
from datetime import datetime, date as DTdate
from app.utils.tools import to_int, finalize_ticket, finalize_transaction
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
# CREAT A NEW TICKET
# ----------------------------
@creator.route("/ticket", methods=["POST"])
@login_required
def create_ticket():
    """ 
    JSON Payload
    {
        "ticket_number": 1234,
        "date": "2026-01-01",
        "location_id": 1,
        "user_id": 1,
        "line_items": [
            {
                "category": "NEW_APPLIANCE",
                "unit_price": 50000,
                "is_return": false
            }
        ],
        "tenders": [
            {
                "payment_type": "CARD",
                "amount": 5000
            }
        ]
    }
    """
    data = request.get_json()
    
    #--------------Check Duplicate Tickets-----------------
    existing = db.session.query(Ticket).filter_by(ticket_number=data.get("ticket_number")).first()
    if existing:
        return jsonify(
            success=False, 
            message=f"Ticket number {existing.ticket_number} already in use.", existing_ticket_number=existing.ticket_number
        ), 400
    
    #-----------------Parse Ticekt Date-----------------------
    ticket_date = datetime.strptime(
        data.get("date", datetime.today().isoformat()), "%Y-%m-%d"
    ).date()
    
    
    #------------------Fetch Location-------------------------
    location = db.session.get(Location, int(data["location_id"]))
    if not location:
        return jsonify(success=False, message="Invali location."), 404
    
    
    #------------------Fetch User---------------------------
    user = db.session.get(User, int(data["user_id"]))
    if not user:
        return jsonify(success=False, message="Invalide user id"), 404
    
    
    #-------------------Create Ticket-----------------------
    ticket = Ticket(
        ticket_number=data["ticket_number"],
        ticket_date=ticket_date,
        location=location,
        user=user
    )
    
    #-------------------Create Transaction---------------------
    transaction = Transaction(
        user=user,
        location=location,
        posted_date=ticket_date
    )
    
    
    #--------------Create Line Items and attach-------------
    for li in data.get("line_items", []):
        try:
            category = SalesCategoryEnum(li["category"])
        except ValueError:
            return jsonify(success=False, message="Invalid category"), 400
        
        taxable, tax_source = determine_taxability(
            category=category,
            location=location
        )
        
        line_item = LineItem(
            category=category,
            unit_price=to_int(li["unit_price"]),
            taxable=taxable,
            taxability_source=tax_source,
            tax_rate=location.current_tax_rate or 0,
            is_return=bool(li.get("is_return", False))
        )
    
        #attach line items to transaction
        line_item.compute_total()
        transaction.line_items.append(line_item)
    # attach it all to the ticket
    transaction.compute_total()
    ticket.transactions.append(transaction)
    
    
    
    #------------------Create Tenders and attach-----------------
    tender_data = data.get("tenders", [])
    
    if not tender_data:
        tender = Tender(
            payment_type=PaymentTypeEnum.CASH,
            amount=transaction.total
        )
        transaction.tenders.append(tender)
    else:
        for t in tender_data:
            try:
                payment_type = PaymentTypeEnum(t["payment_type"])
            except ValueError:
                return jsonify(success=False, message="Invalid payment type"), 400
            
            tender = Tender(
                payment_type=payment_type,
                amount=int(t["amount"])
            )
            transaction.tenders.append(tender)
        
    
    #----------------Compute totals and open balance--------------------
    finalize_ticket(ticket)
    
    
    #-------------------Commit to DB---------------------
    try:
        db.session.add(ticket)
        db.session.commit()
        current_app.logger.info(f"[NEW TICKET]: {user.first_name} {user.last_name} added ticket# {ticket.ticket_number}")
        return jsonify(
            success=True,
            message=f"Ticket added successfully!",
            ticket=ticket.serialize(include_relationships=True)
        ), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[NEW TICKET ERROR]: {e}")
        return jsonify(success=False, message="There was an error when submitting your ticket."), 500




# ----------------------------
# ADD A NEW TRANSACTION TO AN EXISTING TICKET
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
                "sales_category": "USED_APPLIANCE",
                "unit_price": 25000,
                "is_return": False
            }
        ],
        "tenders": [
            {
                "payment_type": "CARD",
                "amount": 25000
            }
        ]
    }
    """
    data = request.get_json()

    # ------------------ Fetch ticket ------------------
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify(success=False, message="Ticket not found"), 404

    # ------------------ Fetch location ------------------
    location = db.session.get(Location, int(data["location_id"]))
    if not location:
        return jsonify(success=False, message="Invalid location"), 404

    # ------------------ Fetch user ------------------
    user = db.session.get(User, int(data["user_id"]))
    if not user:
        return jsonify(success=False, message="User not found"), 404

    # ------------------ Parse transaction date ------------------
    posted_date = datetime.strptime(
        data.get("posted_date", datetime.today().isoformat()), "%Y-%m-%d"
    ).date()

    # ------------------ Create transaction ------------------
    transaction = Transaction(
        user=user,
        location=location,
        posted_date=posted_date
    )

    # ------------------ Create line items ------------------
    for li_data in data.get("line_items", []):
        try:
            category = SalesCategoryEnum(li_data["sales_category"])
        except ValueError:
            return jsonify(success=False, message="Invalid category"), 400

        taxable, tax_source = determine_taxability(
            category=category,
            location=location
        )

        line_item = LineItem(
            category=category,
            unit_price=to_int(li_data["unit_price"]),
            taxable=taxable,
            taxability_source=tax_source,
            tax_rate=location.current_tax_rate or 0,
            is_return=bool(li_data.get("is_return", False))
        )

        transaction.line_items.append(line_item)

    # ------------------ Create tenders ------------------
    for t_data in data.get("tenders", []):
        try:
            payment_type = PaymentTypeEnum(t_data["payment_type"])
        except ValueError:
            return jsonify(success=False, message="Invalid payment type"), 400

        tender = Tender(
            payment_type=payment_type,
            amount=to_int(t_data["amount"])
        )
        transaction.tenders.append(tender)

    # ------------------ Attach transaction to ticket ------------------
    ticket.transactions.append(transaction)

    # ------------------ Compute totals ------------------
    finalize_transaction(transaction)
    ticket.compute_total()

    # ------------------ Commit to DB ------------------
    try:
        db.session.add(transaction)
        db.session.commit()
        current_app.logger.info(
            f"[ADD TRANSACTION]: {user.first_name} {user.last_name} added a transaction to ticket# {ticket.ticket_number}"
        )
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
