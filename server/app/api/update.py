from flask import Blueprint, jsonify, request, current_app
from app.models import Users, EOD
from app.extensions import db
from flask_login import current_user
from datetime import datetime

updater = Blueprint("update", __name__)

def to_int(value):
    """Safely convert any incoming value to int. Fallback = 0."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0

@updater.route("/update_eod/<int:id>", methods=["PATCH"])
def update_eod(id):
    data = request.get_json()
    eod = EOD.query.get(id)
    if not eod:
        current_app.logger.error(f"[EOD ERROR]: Could not locate EOD with ID {id} for update")
        return jsonify(success=False, message="Could not find EOD to update"), 400 
    
    try: 
    
        eod.date = datetime.strptime(data.get("date"), "%Y-%m-%d").date() if data.get("date") else eod.date
        # eod.location = data.get("location").strip()
        eod.units = to_int(data.get("units", eod.units))
        eod.new = to_int(data.get("new", eod.new))
        eod.used = to_int(data.get("used", eod.used))
        eod.extended_warranty = to_int(data.get("extended_warranty", eod.extended_warranty))
        eod.diagnostic_fees = to_int(data.get("diagnostic_fees", eod.diagnostic_fees))
        eod.in_shop_repairs = to_int(data.get("in_shop_repairs", eod.in_shop_repairs))
        eod.ebay_sales = to_int(data.get("ebay_sales", eod.ebay_sales))
        eod.service = to_int(data.get("service", eod.service)  )
        eod.parts = to_int(data.get("parts", eod.parts))
        eod.delivery = to_int(data.get("delivery", eod.delivery)   )
        eod.refunds = to_int(data.get("refunds", eod.refunds))
        eod.ebay_returns = to_int(data.get("ebay_returns", eod.ebay_returns))
        eod.acima = to_int(data.get("acima", eod.acima))
        eod.tower_loan = to_int(data.get("tower_loan", eod.tower_loan))
        eod.card = to_int(data.get("card", eod.card))
        eod.cash = to_int(data.get("cash", eod.cash))
        eod.checks = to_int(data.get("checks", eod.checks))
        
        
        db.session.commit()
        current_app.logger.info(f"{current_user.first_name} updated EOD {id}")
        return jsonify(success=True, message="EOD updated successfully", eod=eod.serialize()), 200
    except Exception as e:
        current_app.logger.error(f"[EOD ERROR]: Error updating EOD with ID {id} - {str(e)}")
        return jsonify(success=False, message="Error updating EOD"), 500