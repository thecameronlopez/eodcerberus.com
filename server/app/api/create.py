from flask import Blueprint, jsonify, request, current_app
from app.models import Users, EOD, Deductions
from app.extensions import db
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta

creator = Blueprint("create", __name__)

def to_int(value):
    """Safely convert any incoming value to int. Fallback = 0."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


@creator.route("/submit_eod", methods=["POST"])
@login_required
def submit_eod():
    data = request.get_json()
    
    duplicate = EOD.query.filter_by(ticket_number=data.get("ticket_number")).first()
    if duplicate:
        return jsonify(success=False, message=f"Ticket number {duplicate.ticket_number} has already been entered"), 409
    
    submitted_as = data.get("submitted_as")
    if submitted_as:
        try:
            user_id = int(submitted_as)
            if not Users.query.get(user_id):
                return jsonify(success=False, message="Invalid user"), 400
        except (ValueError, TypeError):
            return jsonify(success=False, message="Invalid user"), 400
    else:
        user_id = current_user.id

    new_eod = EOD(
        location=data.get("location").strip(),
        ticket_number=to_int(data.get("ticket_number")),
        units=to_int(data.get("units")),
        new=to_int(data.get("new")),
        used=to_int(data.get("used")),
        extended_warranty=to_int(data.get("extended_warranty")),
        diagnostic_fees=to_int(data.get("diagnostic_fees")),
        in_shop_repairs=to_int(data.get("in_shop_repairs")),
        ebay_sales=to_int(data.get("ebay_sales")),
        service=to_int(data.get("service")),
        parts=to_int(data.get("parts")),
        delivery=to_int(data.get("delivery")),
        refunds=to_int(data.get("refunds")),
        ebay_returns=to_int(data.get("ebay_returns")),
        acima=to_int(data.get("acima")),
        tower_loan=to_int(data.get("tower_loan")),
        card=to_int(data.get("card")),
        cash=to_int(data.get("cash")),
        checks=to_int(data.get("checks")),
        date=datetime.strptime(data.get("date"), "%Y-%m-%d").date() if data.get("date") else date.today(),
        user_id=user_id
    )
    

    try:
        db.session.add(new_eod)
        db.session.commit()
        current_app.logger.info(
            f"{current_user.first_name} {current_user.last_name[0]}. submitted an EOD"
        )
        return jsonify(success=True, message="Your EOD has been submitted!"), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[EOD SUBMISSION ERROR]: {e}")
        return jsonify(success=False, message="There was an error submitting your EOD"), 500
     
     
@creator.route("/submit_deduction", methods=["POST"])
@login_required
def submit_deduction():
    data = request.get_json()
    if not data:
        return jsonify(success=False, message="No payload in request"), 400
    
    amount = data.get("amount")
    reason = data.get("reason")
    location = data.get("location")
    date = datetime.strptime(data.get("date"), "%Y-%m-%d").date()
    
    deduction = Deductions(
        amount=to_int(amount),
        user_id=current_user.id,
        date=date,
        reason=reason,
        location=location.strip()
    )
    
    try:
        db.session.add(deduction)
        db.session.commit()
        
        current_app.logger.info(f"{current_user.first_name} {current_user.last_name} submitted a deduction in the amount of {amount}")
        
        return jsonify(success=True, message="Your deduction has been submitted!"), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[DEDUCTION ERROR]: {e}")
        return jsonify(success=False, message="There was an error when submitting deduction"), 500