from flask import Blueprint, jsonify, request, current_app
from app.models import Users, EOD
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

    new_eod = EOD(
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
        cash_deposits=to_int(data.get("cash_deposits")),
        misc_deductions=to_int(data.get("misc_deductions")),
        refunds=to_int(data.get("refunds")),
        ebay_returns=to_int(data.get("ebay_returns")),
        acima=to_int(data.get("acima")),
        tower_loan=to_int(data.get("tower_loan")),
        card=to_int(data.get("card")),
        cash=to_int(data.get("cash")),
        checks=to_int(data.get("checks")),
        date=datetime.strptime(data.get("date"), "%Y-%m-%d").date() if data.get("date") else date.today(),
        user_id=current_user.id
    )

    try:
        db.session.add(new_eod)
        db.session.commit()
        current_app.logger.info(
            f"{current_user.first_name} {current_user.last_name[0]}. submitted an EOD"
        )
        return jsonify(success=True, message="Submitted successfully!"), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[EOD SUBMISSION ERROR]: {e}")
        return jsonify(success=False, message="There was an error submitting your EOD"), 500
     