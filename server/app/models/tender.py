# app/models/tender.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey
from .base import Base

class Tender(Base):
    __tablename__ = "tenders"
    
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), nullable=False)
    payment_type_id: Mapped[int] = mapped_column(ForeignKey("payment_types.id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # ---------------- Relationships ----------------
    transaction = relationship("Transaction", back_populates="tenders", lazy="joined")
    payment_type = relationship("PaymentType", lazy="joined")
    allocations = relationship("LineItemTender", back_populates="tender", cascade="all, delete-orphan")
    
   
