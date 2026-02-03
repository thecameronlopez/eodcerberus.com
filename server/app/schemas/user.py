# app/schemas/user.py
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field, SQLAlchemyAutoSchema
from marshmallow import fields
from app.models import User
from app.extensions import ma

# class UserSchema(SQLAlchemyAutoSchema):
#     class Meta:
#         model = User
#         load_instance = True
#         include_relationships=True
#         exclude = ["password_hash"]
    
#     id = auto_field()
#     first_name = auto_field()
#     last_name = auto_field()
#     email = auto_field()
#     terminated = auto_field()
#     is_admin = auto_field()
#     department = fields.Method("get_department")
#     location = fields.Nested("LocationSchema", exclude=("users",))
    
#     # tickets = fields.Nested("TicketSchema", many=True, exclude=("user",))
#     # transactions = fields.Nested("TransactionSchema", many=True, exclude=("user",))
    
#     def get_department(self, obj):
#         return obj.department.name if obj.department else None
    
    
class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        include_fk = True
        load_instance = True
        
    id = ma.auto_field()
    first_name = ma.auto_field()
    last_name = ma.auto_field()
    email = ma.auto_field()
    terminated = ma.auto_field()
    is_admin = ma.auto_field()
    department = fields.Nested("DepartmentSchema")
    location = fields.Nested("LocationSchema", only=("id", "current_tax_rate", "name"))
    
