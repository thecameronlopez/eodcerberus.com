from app.models import SalesCategory
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma


class CreateSalesCategorySchema(Schema):
    class Meta:
        unknown = "raise"
    
    name = fields.Str(required=True)
    taxable = fields.Bool(required=True)

class SalesCategorySchema(ma.SQLAlchemySchema):
    class Meta:
        model = SalesCategory
        load_instance = True
    
    id = ma.auto_field()
    name = ma.auto_field()
    taxable = ma.auto_field()
    active = ma.auto_field()
    


create_sales_category_schema = CreateSalesCategorySchema()
sales_category_schema = SalesCategorySchema()
many_sales_categories_schema = SalesCategorySchema(many=True) 
