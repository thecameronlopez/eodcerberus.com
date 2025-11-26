from flask import Blueprint, jsonify, request, current_app
from app.models import Users, EOD, Deductions
from app.extensions import db
from flask_login import current_user, login_required
from datetime import datetime, timedelta, date

reader = Blueprint("read", __name__)

def calculate_totals(eods, deductions, include_salesman=None):
    totals = {k: 0 for k in [
        "total_sales", "total_units", "new_appliance_sales", "used_appliance_sales",
        "extended_warranty_sales", "diagnostic_fees", "in_shop_repairs", "service_sales",
        "parts_sales", "ebay_sales", "delivery", "card", "cash", "checks",
        "acima", "tower_loan", "refunds", "ebay_returns", "misc_deductions", "cash_deposits"
    ]}
    if include_salesman:
        totals["salesman"] = include_salesman.serialize()
    for e in eods:
        totals["total_sales"] += e.sub_total
        totals["total_units"] += e.units
        totals["new_appliance_sales"] += e.new
        totals["used_appliance_sales"] += e.used
        totals["extended_warranty_sales"] += e.extended_warranty
        totals["diagnostic_fees"] += e.diagnostic_fees
        totals["in_shop_repairs"] += e.in_shop_repairs
        totals["service_sales"] += e.service
        totals["parts_sales"] += e.parts
        totals["ebay_sales"] += e.ebay_sales
        totals["delivery"] += e.delivery
        totals["card"] += e.card
        totals["cash"] += e.cash
        totals["checks"] += e.checks
        totals["acima"] += e.acima
        totals["tower_loan"] += e.tower_loan
        totals["refunds"] += e.refunds
        totals["ebay_returns"] += e.ebay_returns
        totals["cash_deposits"] += e.cash
    for d in deductions:
        totals["misc_deductions"] += d.amount
    totals["cash_deposits"] -= totals["misc_deductions"]
    return totals


#-----------------------
#----------------------
#
#   GET USERS
#
#-----------------------
#-----------------------
@reader.route("/get_user/<int:id>", methods=["GET"])
def get_user(id):
    user = Users.query.get(id)
    if not user:
        return jsonify(success=False, message="Could not find user in database"), 400
    return jsonify(success=True, user=user.serialize()), 200

@reader.route("/get_users", methods=["GET"])
def get_users():
    users = Users.query.all()
    if not users:
        return jsonify(success=False, message="No users found."), 400
    return jsonify(success=True, users=[u.serialize() for u in users]), 200


#-----------------------
#   GET USERS TOTALS FOR A MONTH
#-----------------------
@reader.route("/monthly_totals", methods=["GET"])
@login_required
def monthly_totals():
    users = Users.query.all()
    if not users:
        return jsonify(success=False, message="There was an error when querying users."), 404
    
    totals = []
    
    for u in users:
        totals.append({
            "id": u.id,
            "total": u.monthly_totals(month_index=date.today().month)
        })
        
    return jsonify(success=True, totals=totals), 200





#------------------------
#------------------------
#
#   GET EODS 
#
#------------------------
#------------------------


#-----------------------
#   GET A SINGLE EOD
#-----------------------
@reader.route("/get_eod/<int:id>", methods=["GET"])
@login_required
def get_eod(id):
    eod = EOD.query.get(id)
    if not eod:
        current_app.logger.error(f"[EOD ERROR]: Could not locate EOD with ID {id}")
        return jsonify(success=False, message="Could not query EOD"), 400
    current_app.logger.info(f"{current_user.first_name} queried for EOD {id}")
    return jsonify(success=True, eod=eod.serialize()), 200



#-----------------------
#   QUERY EODS BY TICKET NUMBER
#-----------------------
@reader.route("/get_eod_by_ticket/<int:ticket_number>", methods=["GET"])
@login_required
def get_eod_by_ticket(ticket_number):
    eod = EOD.query.filter_by(ticket_number=ticket_number).first()
    if not eod:
        current_app.logger.error(f"[EOD ERROR]: Could not locate EOD with Ticket Number {ticket_number}")
        return jsonify(success=False, message="Could not query EOD by ticket number"), 400
    current_app.logger.info(f"{current_user.first_name} queried for EOD with Ticket Number {ticket_number}")
    return jsonify(success=True, eod=eod.serialize()), 200



#-----------------------
#   GET ALL EODS
#-----------------------
@reader.route("/get_all_eods", methods=["GET"])
@login_required
def get_all_eods():
    eods = EOD.query.all()
    if not eods:
        current_app.logger.error(f"[EOD ERROR]: Could not locate EOD with ID {id}")
        return jsonify(success=False, message="EOD's not found"), 400
    return jsonify(success=True, eods=[e.serialize() for e in eods]), 200


#-----------------------
#   GET ALL EODS BY A SPECIFIC USER
#-----------------------
@reader.route("/eods_by_user/<int:user_id>", methods=["GET"])
@login_required
def eods_by_user(user_id):
    eods = EOD.query.filter_by(user_id=user_id).all()
    if not eods:
        return jsonify(success=False, message="No EODs found for this user"), 400
    return jsonify(success=True, eods=[e.serialize() for e in eods]), 200

#-----------------------
#   GET ALL EODS FROM A SPECIFIC DATE
#-----------------------
@reader.route("/eods_by_date", methods=["GET"])
@login_required
def eods_by_date():
    date = request.args.get("date")
    if not date:
        return jsonify(success=False, message="Date is required"), 400
    date = datetime.strptime(date, "%Y-%m-%d").date()
    eods = EOD.query.filter_by(date=date).all()
    if not eods:
        return jsonify(success=False, message="No EOD's found for this date"), 400
    return jsonify(success=True, eods=[e.serialize() for e in eods]), 200

#-----------------------
#   GET ALL EODS IN A SPECIFIC DATE RANGE
#-----------------------
@reader.route("/eod_by_date_range", methods=["GET"])
@login_required
def eod_by_date_range():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    user_id = request.args.get("user_id", type=int)
    
    if not start_date or not end_date:
        return jsonify(success=False, message="Both start_date and end_date are required"), 400
    
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        q = EOD.query.filter(EOD.date.between(start_date, end_date))
        if user_id:
            q = q.filter(EOD.user_id == user_id)

        q = q.order_by(EOD.date.desc())
            
        eods = q.all()
        
        return jsonify(success=True, eods=[e.serialize() for e in eods]), 200
    except Exception as e:
        current_app.logger.error(f"[EOD ERROR]: {str(e)}")
        return jsonify(success=False, message="An error occurred while querying EODs"), 500
    
    
    
#------------------------
#
#   DEDUCTIONS 
#
#------------------------

#-----------------------
#   GET A SINGLE DEDUCTION
#-----------------------
@reader.route("/get_deduction/<int:id>", methods=["GET"])
@login_required
def get_deduction(id):
    deduction = Deductions.query.get(id)
    if not deduction:
        return jsonify(success=False, message="No deduction found."), 400
    return jsonify(success=True, deduction=deduction.serialize()), 200


#-----------------------
#   GET ALL DEDUCTIONS
#-----------------------
@reader.route("/get_deductions", methods=["GET"])
@login_required
def get_deductions():
    deductions = Deductions.query.all()
    return jsonify(success=True, deductions=[d.serialize() for d in deductions]), 200


#-----------------------
#   GET ALL DEDUCTIONS FROM A SPECIFIC USER ON A SPECIFIC DATE
#-----------------------
@reader.route("/get_deductions_by_user/<int:id>", defaults={"date": None}, methods=["GET"])
@reader.route("/get_deductions_by_user/<int:id>/<date>", methods=["GET"])
@login_required
def get_deductions_by_user(id, date):
    query = Deductions.query.filter_by(user_id=id)
    
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter_by(date=date_obj)
        except ValueError:
            return jsonify(success=False, message="Invalid date format."), 400
    deductions = query.all()

    return jsonify(success=True, deductions=[d.serialize() for d in deductions]), 200


#-----------------------
#   GET ALL DEDUCTIONS FROM A SPECIFIC USER IN A DATE RANGE
#-----------------------
@reader.route("/get_deductions_by_date_range/<int:id>", methods=["GET"])
@login_required
def get_deductions_by_date_range(id):
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    query = Deductions.query.filter(Deductions.user_id == id)
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            query = query.filter(Deductions.date.between(start_date, end_date))
        except ValueError:
            return jsonify(success=False, message="Invalid date format."), 400
    elif start_date_str or end_date_str:
        return jsonify(success=False, message="Both start and end date required."), 400
    
    deductions = query.all()
        
    return jsonify(success=True, deductions=[d.serialize() for d in deductions]), 200



#------------------------
#
#   REPORTS 
#
#------------------------

#-----------------------
#   RUN DAILY REPORT FOR A SPECIFIC SALESMAN
#-----------------------
@reader.route("/run_report/<int:id>/<date>", methods=["GET"])
@login_required
def run_report(id, date):
    date = datetime.strptime(date, "%Y-%m-%d").date()
    
    
    eods = EOD.query.filter(EOD.date == date, EOD.user_id == id).all()
    deductions = Deductions.query.filter(Deductions.date == date, Deductions.user_id == id).all()
    salesman = Users.query.get(id)
    if not eods:
        return jsonify(success=False, message="No EOD's match this query"), 400
    
    totals = calculate_totals(eods, deductions, salesman)
    
    current_app.logger.info(f"{current_user.first_name} {current_user.last_name} ran their report")
        
    return jsonify(success=True, totals=totals), 200

@reader.route("/run_report_by_date_range/<int:id>", methods=["GET"])
def run_report_by_date_range(id):
    start_date = datetime.strptime(request.args.get("start_date"), "%Y-%m-%d").date()
    end_date = datetime.strptime(request.args.get("end_date"), "%Y-%m-%d").date()
    
    eods = EOD.query.filter(EOD.user_id == id, EOD.date.between(start_date, end_date)).all()
    deductions = Deductions.query.filter(Deductions.user_id == id, Deductions.date.between(start_date, end_date)).all()
    
    totals = calculate_totals(eods, deductions)
    
    
    return jsonify(success=True, totals=totals), 200


#-----------------------
#   RUN REPORT BY STORE FOR A SPECIFIC DATE
#-----------------------
@reader.route("/run_location_report_by_date/<location>", methods=["GET"])
@login_required
def run_location_report(location):
    date = datetime.strptime(request.args.get("date"), "%Y-%m-%d").date()
    
    eods = EOD.query.filter(EOD.location == location, EOD.date == date).all()
    deductions = Deductions.query.filter(Deductions.date == date, Deductions.location == location).all()
    
    totals = calculate_totals(eods, deductions)
    totals["location"] = location
    
    return jsonify(success=True, totals=totals), 200

#-----------------------
#   RUN A REPORT BY STORE FOR A SINGLE DATE
#-----------------------
@reader.route("/run_location_report_by_date_range/<location>", methods=["GET"])
@login_required
def run_location_report_by_date(location):
    start_date = datetime.strptime(request.args.get("start_date"), "%Y-%m-%d").date()
    end_date = datetime.strptime(request.args.get("end_date"), "%Y-%m-%d").date()
    
    eods = EOD.query.filter(EOD.location == location, EOD.date.between(start_date, end_date)).all()
    deductions = Deductions.query.filter(Deductions.location == location, Deductions.date.between(start_date, end_date)).all()
    
    totals = calculate_totals(eods, deductions)
    totals["location"] = location
    
    return jsonify(success=True, totals=totals), 200

#-----------------------
#   RUN MASTER REPORT FOR A SINGLE DATE
#-----------------------
@reader.route("/run_master_by_date", methods=["GET"])
@login_required
def run_master_report_by_date():
    date = datetime.strptime(request.args.get("date"), "%Y-%m-%d").date()
    
    eods = EOD.query.filter(EOD.date == date).all()
    deductions = Deductions.query.filter(Deductions.date == date).all()
    
    totals = calculate_totals(eods, deductions)    
    
    return jsonify(success=True, totals=totals, master=True), 200

#-----------------------
#   RUN MASTER REPORT FOR A SPECIFIC DATE RANGE
#-----------------------
@reader.route("/run_master_by_date_range", methods=["GET"])
@login_required
def run_master_by_date_range():
    start_date = datetime.strptime(request.args.get("start_date"), "%Y-%m-%d").date()
    end_date = datetime.strptime(request.args.get("end_date"), "%Y-%m-%d").date()
    
    eods = EOD.query.filter(EOD.date.between(start_date, end_date)).all()
    deductions = Deductions.query.filter(Deductions.date.between(start_date, end_date)).all()
    
    totals = calculate_totals(eods, deductions)
    
    return jsonify(success=True, totals=totals, master=True), 200


