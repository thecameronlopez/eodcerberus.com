from app.models import Deduction
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma

class CreateDeductionSchema(Schema):
    class Meta:
        unknown = "raise"
        
    user_id = fields.Int(required=True)
    amount = fields.Int(required=True)
    reason = fields.Str(required=True)



class DeductionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Deduction
        load_instance = False
        
    id = ma.auto_field()
    user_id = ma.auto_field()
    amount = ma.auto_field()
    reason = ma.auto_field()
    date = ma.auto_field()
    
    user = fields.Nested("UserSchema", only=["id", "first_name", "last_name"])
    

create_deduction_schema = CreateDeductionSchema()
deduction_schema = DeductionSchema()
many_deductions_shema = DeductionSchema(many=True)