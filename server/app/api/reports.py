from flask import Blueprint, request
from flask_login import current_user
from app.services.reporting import ReportingService
from app.utils.responses import success
from app.handlers.errors.domain import PermissionDenied
from app.handlers.errors.validation import ValidationError as AppValidationError


bp = Blueprint("reports", __name__)

SUPPORTED_REPORT_TYPES = {"user_eod", "location", "multi_user", "master"}

def parse_int_list(raw_values: list[str], field_name: str) -> list[int]:
    out: list[int] = []
    for raw in raw_values:
        token = (raw or "").strip()
        if not token:
            continue
        try:
            parsed = int(token)
        except ValueError as err:
            raise AppValidationError({field_name: [f"Invalid Integer: '{token}'"]}) from err
        if parsed <= 0:
            raise AppValidationError({field_name: [f"Invalid ID: '{token}'"]})
        out.append(parsed)
    return out



@bp.get("/summary")
def summary_report():
    if not current_user.is_authenticated:
        raise PermissionDenied("Authentication required")
    
    report_type = request.args.get("report_type", "").strip().lower()
    start = (request.args.get("start") or "").strip()
    end = (request.args.get("end") or "").strip() or None
    
    if not report_type:
        raise AppValidationError({"type": ["Report type is required"]})
    if report_type not in SUPPORTED_REPORT_TYPES:
        raise AppValidationError({"type": [f"Report type '{report_type}' not supported"]})
    
    if not start:
        raise AppValidationError({"start": ["Start date is required"]})
    
    users = parse_int_list(request.args.getlist("users", []), "users")
    locations = parse_int_list(request.args.getlist("locations", []), "locations")
    
    if report_type == "user_eod" and not users:
        raise AppValidationError({"users": ["user_eod requires at least one user id."]})
    if report_type == "location" and not locations:
        raise AppValidationError({"locations": ["location report requires at least one location id."]})
    if report_type == "multi_user" and not users:
        raise AppValidationError({"users": ["multi_user report requires one or more user ids."]})
    
    service = ReportingService()
    
    try:
        results = service.build(
            report_type=report_type,
            start=start,
            end=end,
            user_id=users[0] if users else None,
            user_ids=users or None,
            location_id=locations[0] if locations else None,
            location_ids=locations or None,
            include_ticket_details=True,
        )
    except ValueError as err:
        raise AppValidationError({"report": [str(err)]}) from err
    
    return success(
        "Report Generated",
        {
            "report_type": results["report_type"],
            "meta": results["meta"],
            "report": results["report"]
        }
    )