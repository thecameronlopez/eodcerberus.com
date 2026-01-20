from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models import Ticket, LineItem, Transaction, Deduction, User, Location
from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import selectinload

reader = Blueprint("reader", __name__)


# ----------------------------
# GET SINGLE LOCATION
# ----------------------------
@reader.route("/location/<int:location_id>", methods=["GET"])
@login_required
def get_location(location_id):
    location = db.session.get(Location, location_id)
    if not location:
        return jsonify(success=False, message="Location not found."), 404
    return jsonify(success=True, location=location.serialize()), 200


#-------------------
# GET LOCATIONS
#-------------------
@reader.route("/locations", methods=["GET"])
def get_locations():
    locations = db.session.query(Location).order_by(Location.name.asc()).all()
    return jsonify(success=True, locations=[l.serialize() for l in locations]), 200


#-------------------
# GET SINGLE USER
#-------------------
@reader.route("/user/<int:id>", methods=["GET"])
@login_required
def get_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify(success=False, message="User not found"), 404
    
    if user.terminated:
        return jsonify(success=False, message="User has been terminated"), 404
        
    return jsonify(success=True, user=user.serialize()), 200


#-------------------
# GET ALL USERS
#-------------------
@reader.route("/users", methods=["GET"])
@login_required
def get_users():
    users = db.session.query(User).filter(User.terminated == False).order_by(User.last_name, User.first_name).all()
    return jsonify(success=True, users=[u.serialize() for u in users]), 200


#-------------------
# GET TICKET BY TICKET TICKET NUMBER
#-------------------
@reader.route("/ticket/<int:ticket_number>", methods=["GET"])
@login_required
def get_ticket(ticket_number):
    try:
        ticket = db.session.query(Ticket)\
            .options(selectinload(Ticket.transactions).selectinload(Transaction.line_items))\
            .filter_by(ticket_number=ticket_number).first()
        if not ticket:
            return jsonify(success=False, message="Ticket not found"), 404
        return jsonify(success=True, ticket=ticket.serialize(include_relationships=True)), 200
    except Exception as e:
        current_app.logger.error(f"[TICKET QUERY ERROR]: {e}")
        return jsonify(success=False, message="Error when fetching ticket"), 500

#-------------------
# GET TICKETS BY USER AND DATE RANGE
#-------------------
@reader.route("/tickets/user/<int:user_id>", methods=["GET"])
@login_required
def get_tickets_by_user_date_range(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify(success=False, message="User not found."), 404
    
    if user.terminated:
        return jsonify(success=False, message="User has been terminated"), 404
    
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    
    if not start_date_str:
        return jsonify(success=False, message="Start date is required"), 400
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = (
            datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if end_date_str
            else start_date
        )
    except ValueError:
        return jsonify(success=False, message="Invalid date format. Use YYYY-MM-DD"), 400
    
    if start_date > end_date:
        return jsonify(success=False, message="Start date must be before End Date")
    
    tickets = (
        db.session.query(Ticket)
        .options(
            selectinload(Ticket.transactions).selectinload("line_items")
        )
        .filter(
            Ticket.user_id == user_id,
            Ticket.ticket_date.between(start_date, end_date),
        )
        .order_by(Ticket.ticket_date.asc(), Ticket.ticket_number.asc())
        .all()
    )
    
    return jsonify(
        success=True,
        user=user.serialize(),
        tickets=[t.serialize(include_relationships=True) for t in tickets]
    ), 200
    
    
#-------------------
# GET ALL TICKETS IN A DATE RANGE
#-------------------
@reader.route("/tickets", methods=["GET"])
@login_required
def get_tickets_by_date_range():
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    
    if not start_date_str:
        return jsonify(success=False, message="Start date is required"), 400
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = (
            datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if end_date_str
            else start_date
        )
    except ValueError:
        return jsonify(success=False, message="Invalid date format. Use YYYY-MM-DD"), 400
    
    if start_date > end_date:
        return jsonify(success=False, message="Start date must be before End Date")
    
    tickets = (
        db.session.query(Ticket)
        .options(
            selectinload(Ticket.transactions).selectinload(Transaction.line_items)
        )
        .filter(
            Ticket.ticket_date.between(start_date, end_date),
        )
        .order_by(Ticket.ticket_date.asc(), Ticket.ticket_number.asc())
        .all()
    )
    
    return jsonify(
        success=True,
        tickets=[t.serialize(include_relationships=True) for t in tickets]
    ), 200

    

    
#-------------------
# GET DEDUCTIONS BY USER AND DATE RANGE
#-------------------
# client/home/deductions
@reader.route("/deductions/user/<int:user_id>", methods=["GET"])
@login_required
def get_deductions_by_user_date_range(user_id):
    user = db.session.get(User, user_id)
    if not user or user.terminated:
        return jsonify(success=False, message="User not found or terminated."), 404
    
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    
    if not start_date_str:
        return jsonify(success=False, message="Start date is required"), 400
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = (
            datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if end_date_str
            else start_date
        )
    except ValueError:
        return jsonify(success=False, message="Invalid date format. Use YYYY-MM-DD"), 400
    
    if start_date > end_date:
        return jsonify(success=False, message="Start date must be before End Date")
    
    
    deductions = (
        db.session.query(Deduction)
        .filter(
            Deduction.user_id == user_id,
            Deduction.date.between(start_date, end_date)
        )
        .order_by(Deduction.date.asc())
        .all()
    )
    
    return jsonify(
        success=True,
        user=user.serialize(),
        deductions=[d.serialize() for d in deductions]
    ), 200
    
#-------------------
# GET CURRENT DAYS DEDUCTIONS BY USER
#-------------------
#client/home/deductions
@reader.route("/deductions/user/<int:user_id>/today", methods=["GET"])
@login_required
def get_deductions_today(user_id):
    from datetime import datetime
    from app.models import Deduction

    today = datetime.today().date()

    deductions = (
        db.session.query(Deduction)
        .filter(
            Deduction.user_id == user_id,
            Deduction.date == today
        )
        .order_by(Deduction.id.asc())
        .all()
    )

    return jsonify(
        success=True,
        deductions=[d.serialize() for d in deductions]
    ), 200
    
    
#-------------------
# GET ALL DEDUCTIONS BY USER
#-------------------
@reader.route("/deductions/user/<int:user_id>/all", methods=["GET"])
@login_required
def get_all_deductions_by_user(user_id):
    user = db.session.get(User, user_id)
    if not user or user.terminated:
        return jsonify(success=False, message="User not found or terminated."), 404
    
    deductions = (
        db.session.query(Deduction)
        .filter(Deduction.user_id == user_id)
        .order_by(Deduction.date.asc())
        .all()
    )
    
    return jsonify(
        success=True,
        user=user.serialize(),
        deductions=[d.serialize() for d in deductions]
    ), 200

# GET USER MONTHLY TOTALS
# client/home/rankings
@reader.route("/monthly_totals", methods=["GET"])
@login_required
def get_monthly_totals():
    users = (
        db.session.query(User)
        .filter_by(terminated=False)
        .options(
            selectinload(User.transactions).selectinload(Transaction.line_items),
            selectinload(User.deductions)
        )
        .all()
    )
    
    
    
    month_str = request.args.get("month")
    year_str = request.args.get("year")
    
    try:
        month = int(month_str) if month_str else datetime.today().month
        year = int(year_str) if year_str else datetime.today().year
        if not 1 <= month <= 12:
            raise ValueError
    except ValueError:
        return jsonify(success=False, message="Invalid month/year"), 400
    
    department_filter = request.args.get("department")
    
    totals = []
    
    for u in users:
        if department_filter and department_filter.lower() != "all":
            if str(u.department) != department_filter:
                continue
        totals.append({
            "id": u.id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "department": u.department,
            "total": u.month_to_date_total(year, month)
        })
        
    totals.sort(key=lambda x: x["total"], reverse=True)
    
    return jsonify(success=True, totals=totals), 200