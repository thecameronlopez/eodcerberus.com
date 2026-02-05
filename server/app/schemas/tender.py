# app/schemas/tender.py
from marshmallow import fields
from app.models import Tender
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma
from .base import BaseSchema, UpdateSchema


class TenderCreateSchema(BaseSchema):
    class Meta:
        unknown = "raise"
    
    payment_type_id = fields.Int(required=True)
    amount = fields.Int(required=True, validate=validate.Range(min=1))
    

class TenderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tender
        load_instance = False

        
    id = ma.auto_field()
    amount = ma.auto_field()
    transaction_id = ma.auto_field()

    payment_type = fields.Method("get_payment_type")    
    
    def get_payment_type(self, obj):
        return obj.payment_type.name if obj.payment_type else None
    
    
class TenderUpdateSchema(UpdateSchema, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tender
        unknown = "raise"
        load_instance = True
        fields = (
            "amount",
        )


tender_create_schema = TenderCreateSchema()
tender_schema = TenderSchema()
tender_many_schema = TenderSchema(many=True)
tender_update_schema = TenderUpdateSchema()