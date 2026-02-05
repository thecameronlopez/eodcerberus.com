from flask import Blueprint
from app.core.crud_engine import CRUDEngine
from app.core.resource import register_resource

from app.models import Department
from app.schemas.department import (
    department_schema,
    department_create_schema,
    department_update_schema
)


bp = Blueprint("departments", __name__)


department_crud = CRUDEngine(
    model=Department,
    read_schema=department_schema,
    create_schema=department_create_schema,
    update_schema=department_update_schema
)


register_resource(bp, "departments", department_crud)