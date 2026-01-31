# app/schemas/transaction.py
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from app.models import Transaction

class TransactionSchema(SQLAlchemySchema):
    class Meta:
        model = Transaction
        load_instance = True
    
    id = auto_field()
    posted_at = auto_field()
    subtotal = auto_field()
    tax_total = auto_field()
    total = auto_field()
    units = auto_field()
    
    # Computed
    total_paid = fields.Method("get_total_paid")
    balance_delta = fields.Method("get_balance_delta")
    
    # Nested relationships
    line_items = fields.Nested("LineItemSchema", many=True, exclude=("transaction",))
    tenders = fields.Nested("TenderSchema", many=True, exclude=("transaction",))
    
    def get_total_paid(self, obj):
        return obj.total_paid
    
    def get_balance_delta(self, obj):
        return obj.balance_delta
