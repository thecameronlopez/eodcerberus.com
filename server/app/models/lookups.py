from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean
from .base import Base

class SalesCategory(Base):
    __tablename__ = "sales_categories"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    tax_default: Mapped[bool] = mapped_column(Boolean, default=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    line_items = relationship("LineItem", back_populates="category")
    
    
    
    
class PaymentType(Base):
    __tablename__ = "payment_types"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    taxable: Mapped[bool] = mapped_column(Boolean, default=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    tenders = relationship("Tender", back_populates="payment_type")
    
  
    
    
class Department(Base):
    __tablename__ = "departments"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    users = relationship("User", back_populates="department", lazy="selectin")
