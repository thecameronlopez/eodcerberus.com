from flask import Blueprint
from app.core.crud_engine import CRUDEngine
from app.core.resource import register_resource

from app.models import PaymentType
from app.schemas import (
    payment_type_schema,
    payment_type_create_schema,
    payment_type_update_schema
)


bp = Blueprint("payment_types", __name__)


payment_type_crud = CRUDEngine(
    model=PaymentType,
    read_schema=payment_type_schema,
    create_schema=payment_type_create_schema,
    update_schema=payment_type_update_schema
)


register_resource(bp, "payment_types", payment_type_crud)