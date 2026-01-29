from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from app.models import SalesCategory

class SalesCategorySchema(SQLAlchemySchema):
    class Meta:
        model = SalesCategory
        load_instance = True
    
    id = auto_field()
    name = auto_field()
    tax_default = auto_field()
    active = auto_field()
    
