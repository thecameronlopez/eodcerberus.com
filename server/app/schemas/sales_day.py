from app.models import SalesDay
from marshmallow import fields
from app.extensions import ma
from .base import BaseSchema, UpdateSchema

class SalesDayCreateSchema(BaseSchema):
    class Meta:
        unknown = "raise"
        
    user_id = fields.Int(required=True)
    location_id = fields.Int(required=True)
    starting_cash = fields.Int(required=True)
    
    opened_at = fields.DateTime(required=False)
    

class CloseSalesDaySchema(BaseSchema):
    class Meta:
        unknown = "raise"
    
    actual_cash = fields.Int(required=True)
    closed_at = fields.DateTime(required=False)




class SalesDaySchema(ma.SQLAlchemyAutoSchema):
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
    cash_difference = ma.auto_field()
    
    ticket_ids = fields.Method("get_ticket_ids")
    
    def get_ticket_ids(self, obj):
        return [t.id for t in obj.tickets] if obj.tickets else []


    
    
    
class SalesDayDetailSchema(SalesDaySchema):
    user = fields.Nested("UserSchema", only=("id", "first_name", "last_name"))
    location = fields.Nested("LocationSchema", only=("id", "name"))
    tickets = fields.Nested("TicketSchema", many=True, exclude=("sales_day",))
    
class SalesDayUpdateSchema(UpdateSchema, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SalesDay
        load_instance = True
        unknown = "raise"
        

    

sales_day_create_schema = SalesDayCreateSchema()
sales_day_close_schema = CloseSalesDaySchema()
sales_day_schema = SalesDaySchema()
sales_day_detail_schema = SalesDayDetailSchema()
sales_day_many_schema = SalesDaySchema(many=True)
sales_day_update_schema = SalesDayUpdateSchema()
