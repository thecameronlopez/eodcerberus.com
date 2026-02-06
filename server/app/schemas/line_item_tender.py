# app/schemas/line_item_tender.py
from app.models import LineItemTender
from marshmallow import fields
from app.extensions import ma
from .base import BaseSchema, UpdateSchema


class LineItemTenderCreateSchema(BaseSchema):
    class Meta:
        unknown = "raise"
        
    line_item_id = fields.Int(required=True)
    tender_id = fields.Int(required=True)
    applied_pretax = fields.Int(required=False)
    applied_tax = fields.Int(required=False)
    applied_total = fields.Int(required=True)

class LineItemTenderSchema(ma.SQLAlchemyAutoSchema):    
    class Meta:
        model = LineItemTender
        load_instance = False
        
    id = ma.auto_field()
    line_item_id = ma.auto_field()
    tender_id = ma.auto_field()
    applied_pretax = ma.auto_field()
    applied_tax = ma.auto_field()
    applied_total = ma.auto_field()
    

class LineItemTenderUpdateSchema(UpdateSchema, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LineItemTender
        load_instance = True
        unknown = "raise"
        
    

line_item_tender_create_schema = LineItemTenderCreateSchema()
line_item_tender_schema = LineItemTenderSchema()
line_item_tender_many_schema = LineItemTenderSchema(many=True)
line_item_tender_update_schema = LineItemTenderUpdateSchema()
