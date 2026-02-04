# app/schemas/user.py
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.models import User
from app.extensions import ma


class UserRegistrySchema(Schema):
    class Meta:
        unknown = "raise"
        
    first_name = fields.Str(required=True, validate=validate.Length(min=1))
    last_name = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    pw = fields.Str(required=True, load_only=True)
    pw2 = fields.Str(required=True, load_only=True)
    department = fields.Str(required=False)
    is_admin = fields.Bool(required=False)
    location_code = fields.Str(required=False)
    
    @validates_schema
    def validate_password(self, data, **kwargs):
        if data.get("pw") != data.get("pw2"):
            raise ValidationError("Passwords do not match.", field_name="pw2")


class UserLoginSchema(Schema):
    class Meta:
        unknown = "raise"
        
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    
    
    
    
class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        include_fk = True
        load_instance = False
        
    id = ma.auto_field()
    first_name = ma.auto_field()
    last_name = ma.auto_field()
    email = ma.auto_field()
    terminated = ma.auto_field()
    is_admin = ma.auto_field()
    department = fields.Nested("DepartmentSchema")
    location = fields.Nested("LocationSchema", only=("id", "current_tax_rate", "name"))
    

register_user_schema = UserRegistrySchema()
login_schema = UserLoginSchema()
user_schema = UserSchema()
many_users_schema = UserSchema(many=True)