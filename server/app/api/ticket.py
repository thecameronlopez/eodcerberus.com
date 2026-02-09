from flask import Blueprint
from app.core.ticket_crud import TicketCRUDEngine
from app.core.resource import register_resource

from app.models import Ticket
from app.schemas import (
    ticket_schema,
    ticket_detail_schema,
    ticket_create_schema,
    ticket_update_schema
)


bp = Blueprint("tickets", __name__)


ticket_crud = TicketCRUDEngine(
    model=Ticket,
    read_schema=ticket_schema,
    create_schema=ticket_create_schema,
    update_schema=ticket_update_schema
)

ticket_crud.detail_schema = ticket_detail_schema


register_resource(bp, "tickets", ticket_crud)
