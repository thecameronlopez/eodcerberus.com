from flask import Blueprint
from app.core.crud_engine import CRUDEngine
from app.core.resource import register_resource

from app.models import User
from app.schemas import (
    user_schema,
    user_register_schema,
    user_update_schema
)


bp = Blueprint("users", __name__)


user_crud = CRUDEngine(
    model=User,
    read_schema=user_schema,
    create_schema=user_register_schema,
    update_schema=user_update_schema
)


register_resource(bp, "users", user_crud)