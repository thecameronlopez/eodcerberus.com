from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from app.models import SalesDay

class SalesDaySchema(SQLAlchemySchema):
    class Meta:
        model = SalesDay
        load_instance = True

    id = auto_field()
    user_id = auto_field()
    location_id = auto_field()
    opened_at = auto_field()
    closed_at = auto_field()
    status = auto_field()
    starting_cash = auto_field()
    expected_cash = auto_field()
    actual_cash = auto_field()
    cash_difference = auto_field()

    # Nested relationships
    tickets = fields.Nested("TicketSchema", many=True, exclude=("sales_day",))
    user = fields.Nested("UserSchema", only=("id", "first_name", "last_name", "email"))
    location = fields.Nested("LocationSchema")
