from app.models import SalesCategory
from marshmallow import fields, validate
from app.extensions import ma
from .base import BaseSchema, UpdateSchema


class SalesCategoryCreateSchema(BaseSchema):
    class Meta:
        unknown = "raise"
        strip_exclude = {"name"}
    
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    taxable = fields.Bool(required=True)

class SalesCategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SalesCategory
        load_instance = False
        fields = (
            "id",
            "name",
            "taxable",
            "active"
        )


class SalesCategoryUpdateSchema(UpdateSchema, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SalesCategory
        unknown = "raise"
        load_instance = True
        fields = (
            "name",
            "taxable",
            "active"
        )
    


sales_category_create_schema = SalesCategoryCreateSchema()
sales_category_schema = SalesCategorySchema()
sales_category_many_schema = SalesCategorySchema(many=True) 
sales_category_update_schema = SalesCategoryUpdateSchema()
