from app.models import PaymentType
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma


class CreatePaymentTypeSchema(Schema):
    class Meta:
        unknown = "raise"
    
    name = fields.Str(required=True)
    taxable = fields.Bool(required=True)

class PaymentTypeSchema(ma.SQLAlchemySchema):
    class Meta:
        model = PaymentType
        load_instance = True
    
    id = ma.auto_field()
    name = ma.auto_field()
    taxable = ma.auto_field()
    active = ma.auto_field()


create_payment_type_schema = CreatePaymentTypeSchema()  
payment_type_schema = PaymentTypeSchema()
many_payment_types_schema = PaymentTypeSchema(many=True)