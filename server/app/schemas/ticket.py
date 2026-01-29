# app/schemas/ticket.py
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from app.models import Ticket

class TicketSchema(SQLAlchemySchema):
    class Meta:
        model = Ticket
        load_instance = True
    
    id = auto_field()
    ticket_number = auto_field()
    ticket_date = auto_field()
    subtotal = auto_field()
    tax_total = auto_field()
    total = auto_field()
    
    # Computed fields
    is_open = fields.Method("get_is_open")
    total_paid = fields.Method("get_total_paid")
    balance_owed = fields.Method("get_balance_owed")
    
    # Nested transactions (lazy to avoid circular import)
    transactions = fields.Nested("TransactionSchema", many=True, exclude=("ticket",))
    
    def get_is_open(self, obj):
        return obj.is_open
    
    def get_total_paid(self, obj):
        return obj.total_paid
    
    def get_balance_owed(self, obj):
        return obj.balance_owed
