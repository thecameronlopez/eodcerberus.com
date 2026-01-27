from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Date, Boolean, ForeignKey, BigInteger, event
from .base import Base
from datetime import date as DTdate
from .enums import PaymentTypeEnum, PaymentTypeEnumSA

class Tender(Base):
    __tablename__ = "tenders"
    
    # ------------------ Relationships ------------------
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id"), 
        nullable=False
    )
    transaction = relationship(
        "Transaction", 
        back_populates="tenders", 
        lazy="selectin"
    )
    
    # ------------------ Tender Fields ------------------    
    payment_type: Mapped[PaymentTypeEnum] = mapped_column(
        PaymentTypeEnumSA, 
        nullable=False
    )
    amount: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0
    )
    
    # ------------------ Serialize ------------------
    def serialize(self, include_relationships=False):
        data = super().serialize(include_relationships=include_relationships)
        data["payment_type"] = self.payment_type
        data["amount"] = self.amount
        return data