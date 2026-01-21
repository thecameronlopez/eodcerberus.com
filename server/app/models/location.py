from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, Numeric
from .base import Base


class Location(Base):
    __tablename__ = "locations"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    current_tax_rate: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    
    
    users = relationship(
        "User",
        back_populates="location",
        lazy="selectin"
    )
    
    transactions = relationship(
        "Transaction", 
        back_populates="location", 
        lazy="selectin"
    )
    
    tax_rates = relationship(
        "TaxRate",
        back_populates="location",
        cascade="all, delete-orphan",
        lazy="selectin"
    )