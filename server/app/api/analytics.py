from flask import Blueprint, jsonify, request, current_app
from app.models import Users, EOD, Deductions
from app.extensions import db
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from collections import defaultdict

analyzer = Blueprint("analytics", __name__)

from collections import defaultdict
from datetime import datetime

@analyzer.route("/user_analytics/<int:id>", methods=["GET"])
def user_analytics(id):
    start_date = datetime.strptime(request.args.get("start_date"), "%Y-%m-%d").date()
    end_date = datetime.strptime(request.args.get("end_date"), "%Y-%m-%d").date()
    
    eods = EOD.query.filter(EOD.user_id == id, EOD.date.between(start_date, end_date)).all()
    deductions = Deductions.query.filter(Deductions.user_id == id, Deductions.date.between(start_date, end_date)).all()
    
    # Aggregate EODs per date
    chart_data = defaultdict(lambda: {
        "units": 0,
        "card": 0,
        "cash": 0,
        "checks": 0,
        "acima": 0,
        "tower_loan": 0,
        "new": 0,
        "used": 0,
        "extended_warranty": 0,
        "diagnostic_fees": 0,
        "in_shop_repairs": 0,
        "ebay_sales": 0,
        "service": 0,
        "parts": 0,
        "delivery": 0,
        "refunds": 0,
        "ebay_returns": 0,
        "sub_total": 0
    })
    
    for e in eods:
        d = chart_data[e.date]
        d["units"] += e.units
        d["card"] += e.card
        d["cash"] += e.cash
        d["checks"] += e.checks
        d["acima"] += e.acima
        d["tower_loan"] += e.tower_loan
        
        d["new"] += e.new
        d["used"] += e.used
        d["extended_warranty"] += e.extended_warranty
        d["diagnostic_fees"] += e.diagnostic_fees
        d["in_shop_repairs"] += e.in_shop_repairs
        d["ebay_sales"] += e.ebay_sales
        d["service"] += e.service
        d["parts"] += e.parts
        d["delivery"] += e.delivery
        d["refunds"] += e.refunds
        d["ebay_returns"] += e.ebay_returns
        d["sub_total"] += e.sub_total

    # Aggregate deductions per date
    deductions_data = defaultdict(int)
    for d in deductions:
        deductions_data[d.date] += d.amount

    # Merge deductions into chart_data
    for date, amount in deductions_data.items():
        chart_data[date]["deductions"] = amount

    # Convert defaultdict to sorted list for Recharts
    final_data = []
    for date in sorted(chart_data.keys()):
        item = chart_data[date]
        item["date"] = date.strftime("%Y-%m-%d")
        if "deductions" not in item:
            item["deductions"] = 0
        final_data.append(item)

    return jsonify(success=True, data=final_data), 200
