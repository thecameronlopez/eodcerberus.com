from flask import Blueprint
from app.core.crud_engine import CRUDEngine
from app.core.resource import register_resource

from app.models import Tender
from app.schemas import (
    tender_schema,
    tender_create_schema,
    tender_update_schema
)


bp = Blueprint("tenders", __name__)


tender_crud = CRUDEngine(
    model=Tender,
    read_schema=tender_schema,
    create_schema=tender_create_schema,
    update_schema=tender_update_schema
)


register_resource(bp, "tenders", tender_crud)