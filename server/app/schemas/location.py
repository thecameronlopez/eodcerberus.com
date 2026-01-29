# app/schemas/user.py
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from app.models import Location

class LocationSchema(SQLAlchemySchema):
    class Meta:
        model = Location
        load_instance = True
    
    id = auto_field()
    name = auto_field()
    code = auto_field()
    address = auto_field()
    current_tax_rate = auto_field()
    
    users = fields.Nested("UserSchema", many=True)
    