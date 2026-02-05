from flask import Blueprint
from app.core.crud_engine import CRUDEngine
from app.core.resource import register_resource

from app.models import LineItemTender
from app.schemas import (
    line_item_tender_schema,
    line_item_tender_create_schema,
    line_item_tender_update_schema
)


bp = Blueprint("line_item_tenders", __name__)


line_item_tender_crud = CRUDEngine(
    model=LineItemTender,
    read_schema=line_item_tender_schema,
    create_schema=line_item_tender_create_schema,
    update_schema=line_item_tender_update_schema
)


register_resource(bp, "line_item_tenders", line_item_tender_crud)