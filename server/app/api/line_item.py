from flask import Blueprint
from app.core.crud_engine import CRUDEngine
from app.core.resource import register_resource

from app.models import LineItem
from app.schemas import (
    line_item_schema,
    line_item_create_schema,
    line_item_update_schema
)


bp = Blueprint("line_items", __name__)


line_item_crud = CRUDEngine(
    model=LineItem,
    read_schema=line_item_schema,
    create_schema=line_item_create_schema,
    update_schema=line_item_update_schema
)


register_resource(bp, "line_items", line_item_crud)