# app/schemas/tender.py
from marshmallow import fields
from app.models import Tender
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma


class CreateTenderSchema(Schema):
    class Meta:
        unknown = "raise"
    
    payment_type_id = fields.Int(required=True)
    amount = fields.Int(required=True, validate=validate.Range(min=1))
    

class TenderSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Tender
        load_instance = False
    
    id = ma.auto_field()
    amount = ma.auto_field()
    payment_type = fields.Method("get_payment_type")
    
    # Nested allocations
    allocations = fields.Nested("LineItemTenderSchema", many=True, exclude=("tender",))
    
    transaction = fields.Nested("TransactionSchema", dump_only=True, exclude=["line_items", "tenders", "ticket"])
    
    def get_payment_type(self, obj):
        return obj.payment_type.name if obj.payment_type else None


create_tender_schema = CreateTenderSchema()
tender_schema = TenderSchema()
many_tenders_schema = TenderSchema(many=True)