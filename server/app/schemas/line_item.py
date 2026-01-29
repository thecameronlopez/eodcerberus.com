# app/schemas/line_item.py
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields 
from app.models import LineItem
from app.utils.constants import TAXABILITY_SOURCE

class LineItemSchema(SQLAlchemySchema):
    class Meta:
        model = LineItem
        load_instance = True
    
    id = auto_field()
    unit_price = auto_field()
    quantity = auto_field()
    taxable = auto_field()
    taxability_source = auto_field()
    tax_rate = auto_field()
    tax_amount = auto_field()
    total = auto_field()
    is_return = auto_field()
    category = fields.Method("get_category")
    
    # Nested allocations
    payments = fields.Nested("LineItemTenderSchema", many=True, exclude=("line_item",))
    
    def get_category(self, obj):
        return obj.category.value if obj.category else None
    
    def get_taxability_source(self, obj):
        return obj.taxability_source.value if obj.taxability_source else None
    
