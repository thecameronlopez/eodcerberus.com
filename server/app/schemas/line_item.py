# app/schemas/line_item.py
from app.models import LineItem
from app.utils.constants import TAXABILITY_SOURCE
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma


class CreateLineItemSchema(Schema):
    class Meta:
        unknown = "raise"
        
    sales_category_id = fields.Int(required=True)
    unit_price = fields.Int(required=True, validate=validate.Range(min=1))
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    



class LineItemSchema(ma.SQLAlchemySchema):
    class Meta:
        model = LineItem
        load_instance = False
    
    id = ma.auto_field()
    unit_price = ma.auto_field()
    quantity = ma.auto_field()
    taxable = ma.auto_field()
    taxability_source = fields.Method("get_taxability_source")
    tax_rate = ma.auto_field()
    tax_amount = ma.auto_field()
    total = ma.auto_field()
    category = fields.Method("get_category")
    
    # Nested allocations
    allocations = fields.Nested("LineItemTenderSchema", many=True, exclude=("line_item",))
    
    transaction = fields.Nested("TransactionSchema", dump_only=True, exclude=["line_items", "tenders", "ticket"])
    
    def get_category(self, obj):
        return obj.category.name if obj.category else None
    
    def get_taxability_source(self, obj):
        return obj.taxability_source if obj.taxability_source else None
    

create_line_item_schema = CreateLineItemSchema()
line_item_schema = LineItemSchema()
many_line_items_schema = LineItemSchema(many=True)