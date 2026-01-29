# from flask import Blueprint, jsonify, request, current_app
# from flask_login import login_required, current_user
# from app.services.financial_report_service import FinancialReportService
# from datetime import datetime
# from app.extensions import db
# from app.models import User, Location

# reporter = Blueprint("reporter", __name__)

# VALID_REPORT_TYPES = [
#     "operations", "user_eod", "multi_user", "location", "multi_location", "master"
# ]

# def serialize_user(u):
#     return {
#         "id": u.id,
#         "first_name": u.first_name,
#         "last_name": u.last_name
#     }
    
# def serialize_location(l):
#     return {
#         "id": l.id,
#         "name": l.name
#     }

# @reporter.route("/summary", methods=["GET"])
# @login_required
# def operations_report():
#     """  
#     PARAMS
#     start: YYYY-MM-DD
#     end: YYYY-MM-DD
    
#     locations: int or [int]
#     users: int or [int]
#     type: str(report type)
#     """
#     # -------------------------
#     # Parse dates
#     # -------------------------
#     start_str = request.args.get("start")
#     end_str = request.args.get("end")
#     report_type = request.args.get("type", "operations")
    
#     if report_type not in VALID_REPORT_TYPES:
#         return jsonify(success=False, message="Invalid report type"), 400
    
#     if not start_str:
#         return jsonify(success=False, message="Start date is required."), 400
    
#     try:
#         start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
#         end_date = (
#             datetime.strptime(end_str, "%Y-%m-%d").date()
#             if end_str else start_date
#         )
#     except ValueError:
#         return jsonify(success=False, message="Invalid date format, use YYYY-MM-DD"), 400
    
    
#     # -------------------------
#     # Parse filters
#     # -------------------------
#     def parse_ids(param):
#         val = request.args.get(param)
#         if not val:
#             return []
#         try:
#             return [int(v.strip()) for v in val.split(",")]
#         except ValueError:
#             raise ValueError(f"Invalid {param}")
        
#     locations = parse_ids("locations")
#     users = parse_ids("users")
    
#     subject = None
#     if report_type == "user_eod" and len(users) == 1:
#         subject = db.session.get(User, users[0])
#         if not subject:
#             return jsonify(success=False, message="User not found"), 404
        
#     loc = None
#     if report_type == "location" and len(locations) == 1:
#         loc = db.session.get(Location, locations[0])
#         if not loc:
#             return jsonify(success=False, message="Location not found"), 404
        
#     user_meta = []
#     location_meta = []
    
#     if users:
#         user_meta = [
#             serialize_user(u)
#             for u in db.session.query(User)
#             .filter(User.id.in_(users))
#             .all()
#         ]
        
#     if locations:
#         location_meta = [
#             serialize_location(l)
#             for l in db.session.query(Location)
#             .filter(Location.id.in_(locations))
#             .all()
#         ]
   
    
#     # -------------------------
#     # Generate Report
#     # -------------------------  
#     try:
#         service = FinancialReportService(
#             start_date=start_date,
#             end_date=end_date,
#             location_id=locations or None,
#             user_ids=users or None,
#             report_type=report_type,
#             subject=subject
#         )
        
#         report = service.generate()
        
#     except ValueError as e:
#         return jsonify(
#             success=False,
#             message=f"Report validation failed: {str(e)}",
#             err=str(e)
#         )
        
      
#     # -------------------------
#     # Meta data
#     # -------------------------  
#     meta = {
#         "start": start_date.isoformat(),
#         "end": end_date.isoformat(),
#         "locations": location_meta,
#         "users": user_meta,
#         "report_type": report_type
#     }
    
    
#     return jsonify(
#         success=True,
#         meta=meta,
#         report=report
#     )
    
    