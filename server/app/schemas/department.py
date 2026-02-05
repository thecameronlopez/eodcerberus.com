from app.models import Department
from .base import BaseSchema
from marshmallow import fields, Schema, validate, validates_schema, ValidationError, pre_load
from app.extensions import ma



class DepartmentCreateSchema(BaseSchema):
    class Meta:
        unknown = "raise"
    
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50)
    )


class DepartmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Department
    
    
class DepartmentUpdateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Department
        load_instance = True
        unknown = "raise"
        fields = ["name", "active"]
    

create_department_schema = DepartmentCreateSchema() 
update_department_schema = DepartmentUpdateSchema() 
department_schema = DepartmentSchema()
many_departments_schema = DepartmentSchema(many=True)