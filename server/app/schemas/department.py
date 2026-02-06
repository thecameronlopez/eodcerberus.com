from app.models import Department
from .base import BaseSchema, UpdateSchema
from marshmallow import fields, validate
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
        load_instance = False
        fields = ("id", "name", "active")
    
    
class DepartmentUpdateSchema(UpdateSchema, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Department
        load_instance = True
        unknown = "raise"
        fields = ("name", "active")
    

department_create_schema = DepartmentCreateSchema() 
department_update_schema = DepartmentUpdateSchema() 
department_schema = DepartmentSchema()
department_many_schema = DepartmentSchema(many=True)
