from app.extensions import db
from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, Date, ForeignKey, Enum, func, event
from sqlalchemy.orm import relationship
from flask_login import UserMixin
import calendar
from datetime import datetime, date

dpt_enum = Enum("sales", "service", name="department_enum")
location_enum = Enum("lake_charles", "jennings", name="location_enum")

class Users(db.Model, UserMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    department = Column(dpt_enum)
    is_admin = Column(Boolean, server_default='0')
    eods = relationship('EOD', back_populates='salesman', lazy=True) 
    deductions = relationship('Deductions', back_populates="salesman", lazy=True)
    
    def monthly_totals(self, month_index, year=None):
        if year is None:
            year = date.today().year
        
        days_in_month = calendar.monthrange(year, month_index)[1]
        
        start_date = date(year, month_index, 1)
        end_date = date(year, month_index, days_in_month)
        
        total = (
            db.session.query(func.sum(EOD.sub_total))
            .filter(
                EOD.user_id == self.id,
                EOD.date.between(start_date, end_date)
            ).scalar()
        )
        
        return total or 0
        
    
    def serialize(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "department": self.department,
            "is_admin": self.is_admin
        }
        

        

class EOD(db.Model):   
    __tablename__ = "eod"
    
    id = Column(Integer, primary_key=True)
    location = Column(location_enum, nullable=False, server_default="lake_charles")
    ticket_number = Column(BigInteger, nullable=False, unique=True)
    units = Column(Integer, nullable=False) 
    new = Column(Integer, nullable=False, server_default='0')
    used = Column(Integer, nullable=False, server_default='0')
    extended_warranty = Column(Integer, nullable=False, server_default='0')
    diagnostic_fees = Column(Integer, nullable=False, server_default='0')
    in_shop_repairs = Column(Integer, nullable=False, server_default='0')
    ebay_sales = Column(Integer, nullable=False, server_default='0')
    labor = Column(Integer, nullable=False, server_default='0')
    parts = Column(Integer, nullable=False, server_default='0')
    delivery = Column(Integer, nullable=False, server_default='0')
    refunds = Column(Integer, nullable=False, server_default='0')
    ebay_returns = Column(Integer, nullable=False, server_default='0')
    acima = Column(Integer, nullable=False, server_default='0')
    tower_loan = Column(Integer, nullable=False, server_default='0')
    stripe = Column(Integer, nullable=False, server_default='0')
    card = Column(Integer, nullable=False, server_default='0')
    ebay_card = Column(Integer, nullable=False, server_default='0')
    cash = Column(Integer, nullable=False, server_default='0')
    checks = Column(Integer, nullable=False, server_default='0')
    sub_total = Column(Integer, nullable=False, server_default='0')
    
    date = Column(Date, nullable=False)
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    salesman = relationship('Users', back_populates='eods')
    
    __table_args__ = (
        db.Index('idx_eod_date_user', 'date', 'user_id'),
    )
    
    def calculate_sub_total(self):
        revenue_items = [
            self.new,
            self.used,
            self.extended_warranty, 
            self.diagnostic_fees,
            self.in_shop_repairs,
            self.ebay_sales,
            self.labor,
            self.parts,
            self.delivery
        ]
        
        deductions = [
            self.refunds,
            self.ebay_returns
        ]
        
        
        self.sub_total = sum(revenue_items) - sum(deductions)
        
    
    def serialize(self):
        return {
            "id": self.id,
            "location": self.location,
            "ticket_number": self.ticket_number,
            "units": self.units,
            "new": self.new,
            "used": self.used,
            "extended_warranty": self.extended_warranty,
            "diagnostic_fees": self.diagnostic_fees,
            "in_shop_repairs": self.in_shop_repairs,
            "ebay_sales": self.ebay_sales,
            "labor": self.labor,
            "parts": self.parts,
            "delivery": self.delivery,
            "refunds": self.refunds,
            "ebay_returns": self.ebay_returns,
            "acima": self.acima,
            "tower_loan": self.tower_loan,
            "stripe": self.stripe,
            "card": self.card,
            "ebay_card": self.ebay_card,
            "cash": self.cash,
            "checks": self.checks,
            "sub_total": self.sub_total,
            "date": self.date.strftime("%Y-%m-%d"),
            "user_id": self.user_id,
            "salesman": {
                "id": self.salesman.id,
                "first_name": self.salesman.first_name,
                "last_name": self.salesman.last_name,
                "email": self.salesman.email,
                "department": self.salesman.department
            }
        }


class Deductions(db.Model):
    __tablename__ = "deductions"
    
    id = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False, server_default='0')
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    location = Column(location_enum, nullable=False, server_default="lake_charles")
    salesman = relationship("Users", back_populates="deductions")
    
    date = Column(Date, nullable=False)
    reason = Column(Text, nullable=True)
    
    def serialize(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "user_id": self.user_id,
            "location": self.location,
            "date": self.date,
            "reason": self.reason,
            "salesman": {
                "id": self.salesman.id,
                "first_name": self.salesman.first_name,
                "last_name": self.salesman.last_name,
                "email": self.salesman.email,
                "department": self.salesman.department,
            }
        }
    
#Event Listeners
@event.listens_for(EOD, "before_insert")
@event.listens_for(EOD, "before_update")
def before_save(mapper, connection, target):
    target.calculate_sub_total()