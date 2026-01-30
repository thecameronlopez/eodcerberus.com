from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from .base import Base, IDMixin
from datetime import date as DTdate
import calendar
from flask_login import UserMixin

class User(IDMixin, Base, UserMixin):
    __tablename__ = "users"
    
    #Primary Fields
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    terminated: Mapped[bool] = mapped_column(Boolean, default=False)
    
    #Role & Department
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    department = relationship("Department", back_populates="users", lazy="joined")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    #Location
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    location = relationship("Location", back_populates="users", lazy="joined")
    
    #Relationships
    tickets = relationship("Ticket", back_populates="user", lazy="selectin")
    transactions = relationship("Transaction", back_populates="user", lazy="selectin")
    deductions = relationship("Deduction", back_populates="user", lazy="selectin")
    sales_days = relationship("SalesDay", back_populates="user", lazy="selectin")
    
    
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
