from marshmallow import Schema, fields, validate
from datetime import date as DTdate
from app.utils.constants import SALES_CATEGORIES, PAYMENT_TYPES


# app/schemas/create_items.py
from marshmallow import Schema, fields, validate

# -----------------------------
# Line Item for creation
# -----------------------------
class CreateLi(Schema):
    category = fields.Int(required=True)
    unit_price = fields.Int(required=True, validate=validate.Range(min=0))
    quantity = fields.Int(validate=validate.Range(min=1))
    taxable = fields.Bool(required=True)
    is_return = fields.Bool(required=False)


# -----------------------------
# Tender for creation
# -----------------------------
class CreateTender(Schema):
    payment_type = fields.Int(required=True)
    amount = fields.Int(required=True, validate=validate.Range(min=0))


# -----------------------------
# Ticket creation schema
# -----------------------------
class CreateTicket(Schema):
    ticket_number = fields.Int(required=True)
    date = fields.Date(required=True)
    location_id = fields.Int(required=True)
    user_id = fields.Int(required=False)  # Optional, default to current_user in route
    line_items = fields.List(fields.Nested(CreateLi), required=True, validate=validate.Length(min=1))
    tenders = fields.List(fields.Nested(CreateTender))


# -----------------------------
# Transaction creation schema
# -----------------------------
class CreateTransaction(Schema):
    posted_date = fields.Date(required=True)
    location_id = fields.Int(required=True)
    user_id = fields.Int(required=False)  # Optional, default to current_user in route
    line_items = fields.List(fields.Nested(CreateLi), required=True, validate=validate.Length(min=1))
    tenders = fields.List(fields.Nested(CreateTender))



class CreateDepartment(Schema):
    name = fields.String(required=True)
    # active = fields.Boolean(required=False)
 
    
class CreateLocation(Schema):
    name = fields.String(required=True)
    code = fields.String(required=True)
    address = fields.String(required=False)
    current_tax_code = fields.Float(validate=validate.Range(min=0, max=1), required=False)


class CreateSalesCategory(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    
class CreatePaymentType(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    

class CreateDeduction(Schema):
    user_id = fields.Integer(required=True)
    amount = fields.Integer(required=True)
    reason = fields.String(required=True)
    date = fields.Date(required=True)