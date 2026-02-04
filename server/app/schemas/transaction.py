# app/schemas/transaction.py
from marshmallow import fields
from app.models import Transaction, TransactionType
from marshmallow import fields
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma


class CreateTransactionSchema(Schema):
    class Meta:
        unknown = "raise"
        
    
    ticket_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    location_id = fields.Int(required=True)
    
    transaction_type = fields.Str(
        required=False,
        validate=validate.OneOf([t.value for t in TransactionType])
    )
    
    
    

class TransactionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Transaction
        load_instance = False
    
    id = ma.auto_field()
    posted_at = ma.auto_field()
    subtotal = ma.auto_field()
    tax_total = ma.auto_field()
    total = ma.auto_field()
    
    # Computed
    total_paid = fields.Method("get_total_paid")
    balance_delta = fields.Method("get_balance_delta")
    
    # Nested relationships
    line_items = fields.Nested("LineItemSchema", many=True, exclude=("transaction",))
    tenders = fields.Nested("TenderSchema", many=True, exclude=("transaction",))
    ticket = fields.Nested("TicketSchema", only=["ticket_number"], dump_only=True)
    
    def get_total_paid(self, obj):
        return obj.total_paid
    
    def get_balance_delta(self, obj):
        return obj.balance_delta


create_transaction_schema = CreateTransactionSchema()
transaction_schema = TransactionSchema()
many_transactions_schema = TransactionSchema(many=True)