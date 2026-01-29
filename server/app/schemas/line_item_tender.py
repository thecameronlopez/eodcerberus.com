# app/schemas/line_item_tender.py
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from app.models import LineItemTender

class LineItemTenderSchema(SQLAlchemySchema):
    class Meta:
        model = LineItemTender
        load_instance = True
    
    id = auto_field()
    applied_pretax = auto_field()
    applied_tax = auto_field()
    applied_total = auto_field()
    
    line_item_id = auto_field()
    tender_id = auto_field()
    
    # Optional: reference names or amounts
    # sign = fields.Method("get_sign")
    
    def get_sign(self, obj):
        return -1 if obj.line_item.is_return else 1
