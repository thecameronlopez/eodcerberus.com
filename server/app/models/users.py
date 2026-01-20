from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from .enums import DepartmentEnumSA, DepartmentEnum, SalesCategoryEnum, PaymentTypeEnum
from .base import Base
from datetime import date as DTdate
import calendar
from flask_login import UserMixin

class User(Base, UserMixin):
    __tablename__ = "users"
    
    #Primary Fields
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    terminated: Mapped[bool] = mapped_column(Boolean, default=False)
    
    #Role & Department
    department: Mapped[DepartmentEnum] = mapped_column(DepartmentEnumSA, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    #Location
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    location = relationship("Location", back_populates="users", lazy="joined")
    
    #Relationships
    tickets = relationship("Ticket", back_populates="user", lazy="selectin")
    transactions = relationship("Transaction", back_populates="user", lazy="selectin")
    deductions = relationship("Deduction", back_populates="user", lazy="selectin")
    
    
    
    # Computations
    # Compute cash totals for a given date
    def cash_total_for_date(self, date: DTdate):
        """
        total transactions(includes return) - deductions
        """
        total_sales = sum(
            t.total for t in self.transactions if t.posted_date == date
        )
        total_deductions = sum(
            d.amount for d in self.deductions if d.date == date
        )
        
        return total_sales - total_deductions
    
    ##
    def serialize(self, include_ticket=False, include_deductions=False, include_transactions=False):
        """ 
        DEFAULT SERIALIZATION
        """
        data = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "terminated": self.terminated,
            "department": str(self.department),
            "is_admin": self.is_admin,
            "location_id": self.location_id,
            "location": self.location.serialize() if self.location else None
        }
        
        ##
        if include_ticket:
            data["tickets"] = [ticket.serialize(include_relationships=True) for ticket in self.tickets]
        
        if include_deductions:
            data["deductions"] = [deduction.serialize() for deduction in self.deductions]
            
        if include_transactions:
            data["transactions"] = [t.serialize(include_relationships=True) for t in self.transactions]
        
        return data
    

    #----------------
    # Totals for user
    #----------------
    def month_to_date_total(self, year: int, month: int):
        """  
        Return a users net total sales for a given month (after tax and deductions).
        """
        start_date = DTdate(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = DTdate(year, month, last_day)
        
        monthly_line_items = [
            li
            for tx in self.transactions
            if start_date <= tx.posted_date <= end_date
            for li in tx.line_items
        ]
        
        gross_total = sum(li.signed_total for li in monthly_line_items)
        
        total_deductions = sum(d.amount for d in self.deductions if start_date <= d.date <= end_date)
        
        net_total = gross_total - total_deductions
        
        return net_total