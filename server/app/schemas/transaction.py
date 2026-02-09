# app/schemas/transaction.py
from marshmallow import fields, validate
from app.models import Transaction, TransactionType
from app.extensions import ma
from .base import BaseSchema, UpdateSchema
from app.utils.timezone import business_today

class TransactionCreateSchema(BaseSchema):
    class Meta:
        unknown = "raise"
        
    
    ticket_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    location_id = fields.Int(required=True)
    posted_at = fields.Date(required=False, load_default=business_today, format="%Y-%m-%d")
    
    transaction_type = fields.Str(
        required=False,
        load_default=TransactionType.SALE.value,
        validate=validate.OneOf([t.value for t in TransactionType])
    )
    line_items = fields.List(
        fields.Nested("LineItemCreateSchema"),
        required=True,
        validate=validate.Length(min=1),
    )
    tenders = fields.List(
        fields.Nested("TenderCreateSchema"),
        required=True,
        validate=validate.Length(min=1),
    )
    
    

class TransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction
        load_instance = False

    id = ma.auto_field()
    ticket_id = ma.auto_field()
    user_id = ma.auto_field()
    location_id = ma.auto_field()
    transaction_type = ma.auto_field()
    posted_at = ma.auto_field()
    subtotal = ma.auto_field()
    tax_total = ma.auto_field()
    total = ma.auto_field()
    
    # Computed
    total_paid = fields.Method("get_total_paid")
    balance_delta = fields.Method("get_balance_delta")
    line_item_ids = fields.Method("get_line_item_ids")
    
    def get_total_paid(self, obj):
        return obj.total_paid
    
    def get_balance_delta(self, obj):
        return obj.balance_delta
    
    def get_line_item_ids(self, obj):
        return [li.id for li in obj.line_items] if obj.line_items else []
    
    
class TransactionUpdateSchema(UpdateSchema, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction
        load_instance = True
        unknown = "raise"
        fields = ("posted_at", "transaction_type")


transaction_create_schema = TransactionCreateSchema()
transaction_schema = TransactionSchema()
transaction_many_schema = TransactionSchema(many=True)
transaction_update_schema = TransactionUpdateSchema()
