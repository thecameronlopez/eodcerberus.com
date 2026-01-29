from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from app.models import Location, Department

class UserRegistrySchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(min=1))
    last_name = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    pw = fields.Str(required=True, load_only=True)
    pw2 = fields.Str(required=True, load_only=True)
    department = fields.Str(required=True)
    location_code = fields.Str(required=True)
    is_admin = fields.Bool(required=False)
    
    @validates_schema
    def validate_password(self, data, **kwargs):
        if data.get("pw") != data.get("pw2"):
            raise ValidationError("Passwords do not match.", field_name="pw2")
    