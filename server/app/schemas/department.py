from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from app.models import Department

class DepartmentSchema(SQLAlchemySchema):
    class Meta:
        model = Department
        load_instance = True
    
    id = auto_field()
    name = auto_field()
    active = auto_field()
    