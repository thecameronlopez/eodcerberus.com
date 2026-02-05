# app/schemas/line_item.py
from app.models import LineItem
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma
from .base import BaseSchema, UpdateSchema


class LineItemCreateSchema(BaseSchema):
    class Meta:
        unknown = "raise"
        
    sales_category_id = fields.Int(required=True)
    unit_price = fields.Int(required=True, validate=validate.Range(min=1))
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    



class LineItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LineItem
        load_instance = False
        
    id = ma.auto_field()
    unit_price = ma.auto_field()
    quantity = ma.auto_field()
    taxable = ma.auto_field()
    tax_amount = ma.auto_field()
    total = ma.auto_field()
    sales_category_id = ma.auto_field()
    transaction_id = ma.auto_field()
    sales_category_name = fields.Method("get_category_name")
    
    
    def get_category_name(self, obj):
        return obj.sales_category.name if obj.sales_category else None
    
    
    
class LineItemUpdateSchema(UpdateSchema, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LineItem
        load_instance = True
        unknown = "raise"
        fields = (
            "unit_price",
            "quantity",
        )
    

line_item_create_schema = LineItemCreateSchema()
line_item_schema = LineItemSchema()
line_item_many_schema = LineItemSchema(many=True)
line_item_update_schema = LineItemUpdateSchema()