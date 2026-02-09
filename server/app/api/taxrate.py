from flask import Blueprint
from app.core.crud_engine import CRUDEngine
from app.core.resource import register_resource

from app.models import TaxRate
from app.schemas import (
    taxrate_schema,
    taxrate_create_schema,
    taxrate_update_schema
)


bp = Blueprint("taxrates", __name__)


taxrate_crud = CRUDEngine(
    model=TaxRate,
    read_schema=taxrate_schema,
    create_schema=taxrate_create_schema,
    update_schema=taxrate_update_schema
)


register_resource(bp, "taxrates", taxrate_crud, write_admin_only=True)
