from app.models import SalesDay
from marshmallow import fields, Schema, validate, validates_schema, ValidationError
from app.extensions import ma


class CreateSalesDaySchema(Schema):
    class Meta:
        unknown = "raise"
        
    user_id = fields.Int(required=True)
    location_id = fields.Int(required=True)
    starting_cash = fields.Int(required=True)
    
    opened_at = fields.DateTime(required=False)
    

class CloseSalesDaySchema(Schema):
    class Meta:
        unknown = "raise"
    
    actual_cash = fields.Int(required=True)
    closet_at = fields.DateTime(required=False)




class SalesDaySchema(ma.SQLAlchemySchema):
    class Meta:
        model = SalesDay
        load_instance = False

    id = ma.auto_field()
    user_id = ma.auto_field()
    location_id = ma.auto_field()
    opened_at = ma.auto_field()
    closed_at = ma.auto_field()
    status = ma.auto_field()
    starting_cash = ma.auto_field()
    expected_cash = ma.auto_field()
    actual_cash = ma.auto_field()
    cash_difference = ma.auto_field()

    # Nested relationships
    user = fields.Nested("UserSchema", only=("id", "first_name", "last_name"))
    location = fields.Nested("LocationSchema", only=["id", "name"])
    tickets = fields.Nested("TicketSchema", many=True, exclude=("sales_day",))
    

create_sales_day_schema = CreateSalesDaySchema()
close_sales_day_schema = CloseSalesDaySchema()
sales_day_schema = SalesDaySchema()
many_sales_days_schema = SalesDaySchema(many=True)
