from flask import Blueprint
from app.core.crud_engine import CRUDEngine
from app.core.resource import register_resource

from app.models import Deduction
from app.schemas import (
    deduction_schema,
    deduction_create_schema,
    deduction_update_schema
)


bp = Blueprint("deductions", __name__)


deduction_crud = CRUDEngine(
    model=Deduction,
    read_schema=deduction_schema,
    create_schema=deduction_create_schema,
    update_schema=deduction_update_schema
)


register_resource(bp, "deductions", deduction_crud)