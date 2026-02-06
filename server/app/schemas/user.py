# app/schemas/user.py
from marshmallow import fields, validate, validates_schema, ValidationError
from app.models import User
from app.extensions import ma
from .base import BaseSchema, UpdateSchema


class UserBaseInputSchema(BaseSchema):
    class Meta:
        unknown = "raise"
        strip_exclude = {"pw", "pw2", "password"}

    email = fields.Email(required=True)

class UserRegistrySchema(UserBaseInputSchema):
        
    first_name = fields.Str(required=True, validate=validate.Length(min=1))
    last_name = fields.Str(required=True, validate=validate.Length(min=1))
    
    pw = fields.Str(required=True, load_only=True)
    pw2 = fields.Str(required=True, load_only=True)
    
    department = fields.Str(required=False)
    is_admin = fields.Bool(required=False)
    location_code = fields.Str(required=False)
    
    @validates_schema
    def validate_password(self, data, **kwargs):
        if data.get("pw") != data.get("pw2"):
            raise ValidationError("Passwords do not match.", field_name="pw2")


class UserLoginSchema(UserBaseInputSchema):
    password = fields.Str(required=True, load_only=True)
    
    
    
    
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        load_instance = False
        exclude = ("password_hash",)

    id = ma.auto_field()
    first_name = ma.auto_field()
    last_name = ma.auto_field()
    email = ma.auto_field()
    terminated = ma.auto_field()
    is_admin = ma.auto_field()
    
    department = fields.Nested("DepartmentSchema")
    location = fields.Nested("LocationSchema", only=("id", "current_tax_rate", "name"))
    
    
class UserUpdateSchema(UpdateSchema, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        unknown = "raise"
        fields = (
            "first_name",
            "last_name",
            "email",
            "terminated",
            "is_admin",
        )
    
    

user_register_schema = UserRegistrySchema()
user_login_schema = UserLoginSchema()
user_schema = UserSchema()
user_many_schema = UserSchema(many=True)
user_update_schema = UserUpdateSchema()
