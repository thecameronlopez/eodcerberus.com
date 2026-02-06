# app/schemas/user.py
from app.models import Location
from marshmallow import fields, validate
from app.extensions import ma
from .base import BaseSchema, UpdateSchema


class LocationCreateSchema(BaseSchema):
    class Meta:
        unknown = "raise"
        strip_exclude = {"address", "name"}
    
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    code = fields.Str(required=True)
    address = fields.Str(required=False)
    current_tax_rate = fields.Decimal(required=False)

class LocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Location
        load_instance = False
        fields = (
            "id",
            "name",
            "code",
            "address",
            "current_tax_rate",
            "users"
        )
    
    users = fields.Nested("UserSchema", many=True, only=["id", "first_name", "last_name"])
    
    
class LocationUpdateSchema(UpdateSchema, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Location
        load_instance = True
        unknown = "raise"
        fields = (
            "name",
            "code",
            "address",
            "current_tax_rate"
        )
    
    
    
    
location_create_schema = LocationCreateSchema()   
location_schema = LocationSchema()
location_many_schema = LocationSchema(many=True)
location_update_schema = LocationUpdateSchema()
    
