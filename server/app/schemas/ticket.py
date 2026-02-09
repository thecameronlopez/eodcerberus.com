# app/schemas/ticket.py
from marshmallow import fields, validate
from app.models import Ticket
from app.extensions import ma
from .base import BaseSchema, UpdateSchema
from app.utils.timezone import business_today


class TicketCreateSchema(BaseSchema):
    class Meta:
        unknown = "raise"
        
    ticket_number = fields.Int(required=True)
    ticket_date = fields.Date(required=False, load_default=business_today, format="%Y-%m-%d")
    location_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    line_items = fields.List(fields.Nested("LineItemCreateSchema"), required=True, validate=validate.Length(min=1))
    tenders = fields.List(fields.Nested("TenderCreateSchema"), required=True)
    transaction_type = fields.Str(required=True)




class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = False

        
    id = ma.auto_field()
    ticket_number = ma.auto_field()
    ticket_date = ma.auto_field()
    subtotal = ma.auto_field()
    tax_total = ma.auto_field()
    total = ma.auto_field()
    location_id = ma.auto_field()
    user_id = ma.auto_field()
    sales_day_id = ma.auto_field()

    
    # Computed fields
    is_open = fields.Method("get_is_open")
    total_paid = fields.Method("get_total_paid")
    balance_owed = fields.Method("get_balance_owed")
    
    def get_is_open(self, obj):
        return obj.is_open
    
    def get_total_paid(self, obj):
        return obj.total_paid
    
    def get_balance_owed(self, obj):
        return obj.balance_owed
    
    
class TicketDetailSchema(TicketSchema):
    transactions = fields.Nested("TransactionSchema", many=True, dump_only=True)
    line_items = fields.Nested("LineItemSchema", many=True, dump_only=True)
    tenders = fields.Nested("TenderSchema", many=True, dump_only=True)
    sales_day = fields.Nested("SalesDaySchema", dump_only=True)
    location = fields.Nested("LocationSchema", dump_only=True, only=("id", "name"))
    user = fields.Nested("UserSchema", dump_only=True, only=("id", "first_name", "last_name"))
    
    
    
class TicketUpdateSchema(UpdateSchema, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = True
        unknown = "raise"
        fields = (
            "ticket_number",
            "ticket_date",
        )


ticket_create_schema = TicketCreateSchema()
ticket_schema = TicketSchema()
ticket_detail_schema = TicketDetailSchema()
ticket_many_schema = TicketSchema(many=True)
ticket_update_schema = TicketUpdateSchema()
