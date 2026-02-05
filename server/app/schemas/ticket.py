# app/schemas/ticket.py
from marshmallow import fields
from app.models import Ticket
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma


class CreateTicketSchema(Schema):
    class Meta:
        unknown = "raise"
        
    ticket_number = fields.Int(required=True)
    date = fields.Date(required=True, format="%Y-%m-%d")
    location_id = fields.Int(required=True)
    user_id = fields.Int(required=False)  # Optional, default to current_user in route
    line_items = fields.List(fields.Nested("CreateLineItemSchema"), required=True, validate=validate.Length(min=1))
    tenders = fields.List(fields.Nested("CreateTenderSchema"))
    transaction_type = fields.Str(required=True)




class TicketSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Ticket
        load_instance = False
    
    id = ma.auto_field()
    ticket_number = ma.auto_field()
    ticket_date = ma.auto_field()
    subtotal = ma.auto_field()
    tax_total = ma.auto_field()
    total = ma.auto_field()
    
    # Computed fields
    is_open = fields.Method("get_is_open")
    total_paid = fields.Method("get_total_paid")
    balance_owed = fields.Method("get_balance_owed")
    
    # Nested transactions (lazy to avoid circular import)
    transactions = fields.Nested("TransactionSchema", many=True, exclude=("ticket",))
    sales_day = fields.Nested("SalesDaySchema", dump_only=True, exclude=["tickets"])
    
    def get_is_open(self, obj):
        return obj.is_open
    
    def get_total_paid(self, obj):
        return obj.total_paid
    
    def get_balance_owed(self, obj):
        return obj.balance_owed


create_ticket_schema = CreateTicketSchema()
ticket_schema = TicketSchema()
many_tickets_schema = TicketSchema(many=True)