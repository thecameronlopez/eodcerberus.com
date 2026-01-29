from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from app.models import PaymentType

class PaymentTypeSchema(SQLAlchemySchema):
    class Meta:
        model = PaymentType
        load_instance = True
    
    id = auto_field()
    name = auto_field()
    taxable = auto_field()
    active = auto_field()
    
