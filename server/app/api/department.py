from flask import Blueprint
from app.core.crud_engine import CRUDEngine
from app.core.resource import register_resource

from app.models import Department
from app.schemas.department import (
    department_schema,
    create_department_schema,
    update_department_schema
)


bp = Blueprint("department", __name__)


department_crud = CRUDEngine(
    model=Department,
    read_schema=department_schema,
    create_schema=create_department_schema,
    update_schema=update_department_schema
)


register_resource(bp, "department", department_crud)