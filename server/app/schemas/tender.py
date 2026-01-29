# app/schemas/tender.py
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from app.models import Tender

class TenderSchema(SQLAlchemySchema):
    class Meta:
        model = Tender
        load_instance = True
    
    id = auto_field()
    amount = auto_field()
    payment_type = fields.Method("get_payment_type")
    
    # Nested allocations
    allocations = fields.Nested("LineItemTenderSchema", many=True, exclude=("tender",))
    
    def get_payment_type(self, obj):
        return obj.payment_type.value if obj.payment_type else None
