# app/schemas/user.py
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field, SQLAlchemyAutoSchema
from marshmallow import fields
from app.models import User

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_relationships=True
        exclude = ["password_hash"]
    
    id = auto_field()
    first_name = auto_field()
    last_name = auto_field()
    email = auto_field()
    terminated = auto_field()
    is_admin = auto_field()
    department = fields.Method("get_department")
    location = fields.Nested("LocationSchema", exclude=("users",))
    
    # tickets = fields.Nested("TicketSchema", many=True, exclude=("user",))
    # transactions = fields.Nested("TransactionSchema", many=True, exclude=("user",))
    
    def get_department(self, obj):
        return obj.department.name if obj.department else None
    
    
