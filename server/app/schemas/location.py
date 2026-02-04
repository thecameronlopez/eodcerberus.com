# app/schemas/user.py
from app.models import Location
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma


class CreateLocationSchema(Schema):
    class Meta:
        unknown = "raise"
    
    name = fields.Str(required=True)
    code = fields.Str(required=True)
    address = fields.Str(required=False)
    current_tax_rate = fields.Decimal(required=False)

class LocationSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Location
        load_instance = False
    
    id = ma.auto_field()
    name = ma.auto_field()
    code = ma.auto_field()
    address = ma.auto_field()
    current_tax_rate = ma.auto_field()
    
    users = fields.Nested("UserSchema", many=True, only=["id", "first_name", "last_name"])
    
    
    
    
create_location_schema = CreateLocationSchema()   
location_schema = LocationSchema()
many_locations_schema = LocationSchema(many=True)
    