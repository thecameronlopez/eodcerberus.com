from flask import Blueprint
from app.core.crud_engine import CRUDEngine
from app.core.resource import register_resource

from app.models import SalesDay
from app.schemas import (
    sales_day_schema,
    sales_day_create_schema,
    sales_day_update_schema
)


bp = Blueprint("sales_days", __name__)


sales_day_crud = CRUDEngine(
    model=SalesDay,
    read_schema=sales_day_schema,
    create_schema=sales_day_create_schema,
    update_schema=sales_day_update_schema
)


register_resource(bp, "sales_days", sales_day_crud)