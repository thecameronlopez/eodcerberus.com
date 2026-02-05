from app.models import PaymentType
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma
from .base import BaseSchema, UpdateSchema


class PaymentTypeCreateSchema(BaseSchema):
    class Meta:
        unknown = "raise"
        strip_exclude = {"name"}
    
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    taxable = fields.Bool(required=True)

class PaymentTypeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentType
        load_instance = False
        fields = (
            "id",
            "name",
            "taxable",
            "active"
        )


class PaymentTypeUpdateSchema(UpdateSchema, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentType
        load_instance = True
        unknown = "raise"
        fields = (
            "name",
            "taxable",
            "active"
        )


payment_type_create_schema = PaymentTypeCreateSchema()  
payment_type_schema = PaymentTypeSchema()
payment_types_many_schema = PaymentTypeSchema(many=True)
payment_type_update_schema = PaymentTypeUpdateSchema()