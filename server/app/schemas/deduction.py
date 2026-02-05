from app.models import Deduction
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma
from .base import BaseSchema, UpdateSchema

class DeductionCreateSchema(BaseSchema):
    class Meta:
        unknown = "raise"
        
    user_id = fields.Int(required=True)
    amount = fields.Int(required=True, validate=validate.Range(min=1))
    reason = fields.Str(required=True)



class DeductionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Deduction
        load_instance = False
        
    
    user = fields.Nested("UserSchema", only=["id", "first_name", "last_name"])
    
    
class DeductionUpdateSchema(UpdateSchema, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Deduction
        load_instance = True
        unknown = "raise"
        fields = ("amount", "reason", "date")
        
    

deduction_create_schema = DeductionCreateSchema()
deduction_schema = DeductionSchema()
deduction_many_schema = DeductionSchema(many=True)
deduction_update_schema = DeductionUpdateSchema()