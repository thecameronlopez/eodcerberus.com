from app.models import Department
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma



class CreateDepartmentSchema(Schema):
    class Meta:
        unknown = "raise"
    
    name = fields.Str(required=True)


class DepartmentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Department
        load_instance = True
    
    id = ma.auto_field()
    name = ma.auto_field()
    active = ma.auto_field()
    

create_department_schema = CreateDepartmentSchema()  
department_schema = DepartmentSchema()
many_departments_schema = DepartmentSchema(many=True)