# app/schemas/line_item_tender.py
from marshmallow_sqlalchemy import auto_field
from app.models import LineItemTender
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma


class CreateLineItemTenderSchema(Schema):
    class Meta:
        unknown = "raise"
        
    line_item_id = fields.Int(required=True)
    tender_id = fields.Int(required=True)
    applied_pretax = fields.Int(required=False)
    applied_tax = fields.Int(required=False)
    applied_total = fields.Int(required=True)

class LineItemTenderSchema(ma.SQLAlchemySchema):    
    class Meta:
        model = LineItemTender
        load_instance = False
        
    id = ma.auto_field()
    
    line_item_id = ma.auto_field()
    tender_id = ma.auto_field()
    applied_pretax = ma.auto_field()
    applied_tax = ma.auto_field()
    applied_total = ma.auto_field()
    
    line_item = fields.Nested("LineItemSchema", exclude=("allocations",))
    tender = fields.Nested("TenderSchema", exclude=("allocations",))
    
    

create_line_item_tender_schema = CreateLineItemTenderSchema()
line_item_tender_schema = LineItemTenderSchema()
many_line_item_tenders_schema = LineItemTenderSchema(many=True)