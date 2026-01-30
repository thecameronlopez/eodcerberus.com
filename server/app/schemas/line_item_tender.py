# app/schemas/line_item_tender.py
from marshmallow_sqlalchemy import auto_field
from marshmallow import fields, Schema
from app.models import LineItemTender

class LineItemTenderSchema(Schema):    
    applied_pretax = fields.Int()
    applied_tax = fields.Int()
    applied_total = fields.Int()
    
    line_item_id = fields.Int(required=True)
    tender_id = fields.Int(required=True)
    
    # Optional: reference names or amounts
    # sign = fields.Method("get_sign")
    
    def get_sign(self, obj):
        return -1 if obj.line_item.is_return else 1
