from app.models import TaxRate
from marshmallow import fields
from app.extensions import ma
from .base import BaseSchema, UpdateSchema

class TaxRateCreateSchema(BaseSchema):
    class Meta:
        unknown = "raise"
        
    location_id = fields.Int(required=True)
    rate = fields.Decimal(required=True)
    effective_from = fields.Date(required=True)
    effective_to = fields.Date(required=False)
    
    
    

class TaxRateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TaxRate
        load_instance = False

    id = ma.auto_field()
    location_id = ma.auto_field()
    rate = ma.auto_field()
    effective_from = ma.auto_field()
    effective_to = ma.auto_field()
    
    location = fields.Nested("LocationSchema", only=["id", "name", "current_tax_rate"])
    
    

class TaxRateUpdateSchema(UpdateSchema, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TaxRate
        load_instance = True
        unknown = "raise"
        fields = (
            "rate",
        )
    

taxrate_create_schema = TaxRateCreateSchema()
taxrate_schema = TaxRateSchema()
taxrate_many_schema = TaxRateSchema(many=True)
taxrate_update_schema = TaxRateUpdateSchema()
