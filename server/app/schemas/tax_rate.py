from app.models import TaxRate
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma

class CreateTaxRateSchema(Schema):
    class Meta:
        unknown = "raise"
        
    location_id = fields.Int(required=True)
    rate = fields.Decimal(required=True)
    effective_from = fields.Date(required=True)
    effective_to = fields.Date(required=False)
    
    
    

class TaxRateSchema(ma.SQLAlchemySchema):
    class Meta:
        model = TaxRate
        load_instance = False
        
    id = ma.auto_field()
    location_id = ma.auto_field()
    rate = ma.auto_field()
    effective_from = ma.auto_field()
    effective_to = ma.auto_field()
    
    location = fields.Nested("LocationSchema", only=["id", "name", "current_tax_rate"])
    
    

create_taxrate_schema = CreateTaxRateSchema()
taxrate_schema = TaxRateSchema()
many_taxrates_schema = TaxRateSchema(many=True)