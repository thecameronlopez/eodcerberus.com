# app/schemas/user.py
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from app.models import User

class UserSchema(SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True
    
    id = auto_field()
    first_name = auto_field()
    last_name = auto_field()
    email = auto_field()
    terminated = auto_field()
    is_admin = auto_field()
    department = fields.Method("get_department")
    
    tickets = fields.Nested("TicketSchema", many=True, exclude=("user",))
    transactions = fields.Nested("TransactionSchema", many=True, exclude=("user",))
    
    def get_department(self, obj):
        return obj.department.value if obj.department else None
