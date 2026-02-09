from flask import Blueprint
from app.core.crud_engine import CRUDEngine
from app.core.resource import register_resource

from app.models import SalesCategory
from app.schemas import (
    sales_category_schema,
    sales_category_create_schema,
    sales_category_update_schema
)


bp = Blueprint("sales_categories", __name__)


sales_category_crud = CRUDEngine(
    model=SalesCategory,
    read_schema=sales_category_schema,
    create_schema=sales_category_create_schema,
    update_schema=sales_category_update_schema
)


register_resource(bp, "sales_categories", sales_category_crud, write_admin_only=True)
