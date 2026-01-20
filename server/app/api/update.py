from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models import Ticket, LineItem, Deduction, User, Location, TaxRate, Transaction, SalesCategoryEnum, TaxabilitySourceEnum
from app.extensions import db
from datetime import datetime, timedelta, date
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.utils.tools import to_int

updator = Blueprint("update", __name__)

#-------------------
# UPDATE USER INFO
#-------------------
@updator.route("/user/<int:user_id>", methods=["PATCH"])
@login_required
def update_user_info(user_id):
    data = request.get_json()
    if not data:
        return jsonify(success=False, message="Invalid JSON payload"), 400

    # Only allow admins to update other users (optional rule)
    if user_id != current_user.id and not current_user.is_admin:
        return jsonify(success=False, message="Unauthorized"), 403

    # Retrieve user
    user = db.session.get(User, user_id)
    if not user:
        return jsonify(success=False, message="User not found"), 404

    # Fields that can be updated
    updatable_fields = ["first_name", "last_name", "email", "department", "is_admin"]

    try:
        for field in updatable_fields:
            if field in data:
                # Handle enums for department
                if field == "department":
                    from app.models import DepartmentEnum
                    try:
                        user.department = DepartmentEnum(data[field])
                    except ValueError:
                        return jsonify(success=False, message=f"Invalid department value: {data[field]}"), 400
                elif field == "is_admin":
                    user.is_admin = bool(data[field])
                else:
                    setattr(user, field, data[field])

        db.session.commit()
        current_app.logger.info(f"[USER UPDATE] {current_user.id} updated user {user_id}")
        return jsonify(success=True, message="User info updated successfully", user=user.serialize()), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[USER UPDATE ERROR]: {e}")
        return jsonify(success=False, message="Error updating user info"), 500

    


#-------------------
# UPDATE USER TERMINATION STATUS
#-------------------
@updator.route("/user/<int:user_id>/terminate", methods=["PUT"])
@login_required
def update_user_termination(user_id):

    # Only allow admins to terminate users (optional but recommended)
    if not current_user.is_admin:
        return jsonify(success=False, message="Unauthorized"), 403

    # Retrieve user
    user = db.session.get(User, user_id)
    if not user:
        return jsonify(success=False, message="User not found"), 404
    if user.id == current_user.id:
        return jsonify(success=False, message="Cannot terminate own account"), 400


    try:
        user.terminated = not bool(user.terminated)
        db.session.commit()

        action = "terminated" if user.terminated else "reactivated"
        current_app.logger.info(f"[USER STATUS] {current_user.first_name} set user {user_id} as {action}")

        return jsonify(success=True, message=f"User {action} successfully", user=user.serialize()), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[USER TERMINATION ERROR]: {e}")
        return jsonify(success=False, message="Error updating user status"), 500


#-------------------
# UPDATE USER DEFAULT LOCATION
#-------------------
@updator.route("/user/location/<int:user_id>", methods=["PATCH"])
@login_required
def update_user_location(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify(success=False, message="User not found"), 404
    location_id = request.args.get("location_id")
    if not location_id:
        return jsonify(success=False, message="Missing paramater: location_id"), 400
    location = db.session.get(Location, location_id)
    if not location:
        return jsonify(success=False, message="Location not found"), 404
    user.location = location
    try:
        db.session.commit()
        current_app.logger.info(f"{current_user.first_name} {current_user.last_name} updated their location to {location.name}")
        return jsonify(success=True, message="Location updated successfully", location=location.serialize()), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[USER LOCATION UPDATE ERROR]: {e}")
        return jsonify(success=False, message="Error when updating user location"), 500



#-------------------
# HANDLE RETURNS
#-------------------
@updator.route("/return/<int:ticket_id>", methods=["POST"])
@login_required
def create_return(ticket_id):
    data = request.get_json()
    
    ticket = db.session.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    ).scalar_one_or_none()
    
    if not ticket:
        return jsonify(success=False, message="Ticket not found"), 404
    
    # valdate location
    location = db.session.get(Location, data["location_id"])
    if not location:
        return jsonify(success=False, message="Location not found"), 404
    
    posted_date = datetime.strptime(data.get("posted_date"), "%Y-%m-%d").date() if data.get("posted_date") else datetime.today().date()
    
    # create return transaction
    transaction = Transaction(
        ticket=ticket,
        user_id=current_user.id,
        location_id=location.id,
        posted_date=posted_date
    )
    
    for li in data.get("line_items", []):
        try:
            category = SalesCategoryEnum(li["category"])
            tax_source = TaxabilitySourceEnum(li["taxability_source"])
        except ValueError:
            return jsonify(success=False, message="Invalid category or taxability source"), 400

        transaction.line_items.append(
            LineItem(
                transaction=transaction,
                description=li["description"],
                category=category,
                quantity=to_int(li.get("quantity", 1)),
                unit_price=to_int(li["unit_price"]),
                taxable=li.get("taxable", True),
                taxability_source=tax_source,
                is_return=True
            )
        )
    ticket.transactions.append(transaction)
    
    try:
        db.session.add(transaction)
        db.session.commit()
        current_app.logger.info(f"[RETURN CREATED]: {current_user.first_name} {current_user.last_name} has processed a return for ticket# {ticket.ticket_number}")
        return jsonify(success=True, message="Return transaction created successfully!", transaction=transaction.serialize(include_relationships=True)), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[RETURN CREATION ERROR]: {e}")
        return jsonify(success=False, message="Error when processing return"), 500

    


#-------------------
# UPDATES LINE ITEM INFO
#-------------------
@updator.route("/line_item/<int:line_item_id>", methods=["PATCH"])
@login_required
def update_line_item(line_item_id):
    data = request.get_json()
    line_item = db.session.get(LineItem, line_item_id)
    if not line_item:
        return jsonify(success=False, message="Line item not found."), 404
    
    sales_category = data.get("sales_category")
    payment_type = data.get("payment_type")
    amount = data.get("amount")
    is_return = data.get("is_return")
    date_str = data.get("date")
    
    if "description" in data:
        line_item.description = data["description"]
    if "quantity" in data:
        line_item.quantity = to_int(data["quantity"])
    if "unit_price" in data:
        line_item.unit_price = to_int(data["unit_price"])
    if "taxable" in data:
        line_item.taxable = bool(data["taxable"])
    if "taxability_source" in data:
        try:
            line_item.taxability_source = TaxabilitySourceEnum(data["taxability_source"])
        except ValueError:
            return jsonify(success=False, message="Invalid taxability source"), 400
    if "is_return" in data:
        line_item.is_return = bool(data["is_return"])
        
    try:
        db.session.commit()
        return jsonify(success=True, message="Line item updated successfully!", line_item=line_item.serialize()), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[LINE ITEM UPDATE ERROR]: {e}")
        return jsonify(success=False, message="Error when updating line item"), 500
    
    
#-------------------
# UPDATES DEDUCTION INFO
#-------------------
@updator.route("/deduction/<int:deduction_id>", methods=["PUT"])
@login_required
def update_deduction(deduction_id):
    data = request.get_json()
    deduction = db.session.get(Deduction, deduction_id)
    if not deduction:
        return jsonify(success=False, message="Deduction not found"), 404

    amount = data.get("amount")
    reason = data.get("reason")
    date_str = data.get("date")

    if amount is not None:
        deduction.amount = amount
    if reason:
        deduction.reason = reason
    if date_str:
        try:
            deduction.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify(success=False, message="Invalid date format. Use YYYY-MM-DD"), 400

    try:
        db.session.commit()
        return jsonify(success=True, message="Deduction updated successfully", deduction=deduction.serialize()), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[DEDUCTION UPDATE ERROR]: {e}")
        return jsonify(success=False, message="Error updating deduction"), 500


#-------------------
# UPDATES LOCATION INFO
#-------------------
@updator.route("/location/<int:location_id>", methods=["PUT"])
@login_required
def update_location(location_id):
    location = db.session.get(Location, location_id)
    if not location:
        return jsonify(success=False, message="Location not found."), 404
    
    data = request.get_json()
    new_name = (data.get("name") or location.name).strip().title()
    new_code = (data.get("code") or location.code).strip().lower()
    new_address = data.get("address") or location.address
    new_tax_rate = data.get("current_tax_rate")
    
    if new_tax_rate is not None:
        try:
            new_tax_rate = float(new_tax_rate)
            if new_tax_rate < 0 or new_tax_rate > 1:
                raise ValueError
        except ValueError:
            return jsonify(success=False, message="Invalid tax rate."), 400
    else:
        new_tax_rate = location.current_tax_rate or 0.0
    
    
    existing = db.session.query(Location).filter(
        ((Location.name == new_name) | (Location.code == new_code)) &
        (Location.id != location.id)
    ).first()
    if existing:
        return jsonify(success=False, message="Name or code already in use"), 409
    
    location.name = new_name
    location.code = new_code
    location.address = new_address
    
    if location.current_tax_rate != new_tax_rate:
        today = date.today()
        active_rate = (
            db.session.query(TaxRate)
            .filter(TaxRate.location_id == location.id, TaxRate.effective_to.is_(None))
            .order_by(TaxRate.effective_from.desc())
            .first()
        )
        if active_rate:
            active_rate.effective_to = today - timedelta(days=1)
            
        new_tax = TaxRate(
            location=location,
            rate=new_tax_rate,
            effective_from=today,
            effective_to=None
        )
        db.session.add(new_tax)
        location.current_tax_rate = new_tax_rate
    
    try:
        db.session.commit()
        current_app.logger.info(f"[LOCATION UPDATED]: {current_user.first_name} {current_user.last_name} updated location '{location.name}'")
        return jsonify(success=True, message="Location has been updated!", new_location=location.serialize()), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[LOCATION UPDATE ERROR]: {e}")
        return jsonify(success=False, message="Error when updating location"), 500