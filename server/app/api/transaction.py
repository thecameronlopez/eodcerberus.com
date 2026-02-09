from flask import Blueprint
from app.core.transaction_crud import TransactionCRUDEngine
from app.core.resource import register_resource

from app.models import Transaction
from app.schemas import (
    transaction_schema,
    transaction_create_schema,
    transaction_update_schema
)


bp = Blueprint("transactions", __name__)


transaction_crud = TransactionCRUDEngine(
    model=Transaction,
    read_schema=transaction_schema,
    create_schema=transaction_create_schema,
    update_schema=transaction_update_schema
)


register_resource(bp, "transactions", transaction_crud)
