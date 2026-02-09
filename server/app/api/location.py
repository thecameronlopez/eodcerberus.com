from flask import Blueprint
from app.core.crud_engine import CRUDEngine
from app.core.resource import register_resource

from app.models import Location
from app.schemas import (
    location_schema,
    location_create_schema,
    location_update_schema
)


bp = Blueprint("locations", __name__)


location_crud = CRUDEngine(
    model=Location,
    read_schema=location_schema,
    create_schema=location_create_schema,
    update_schema=location_update_schema
)


register_resource(bp, "locations", location_crud, write_admin_only=True)
