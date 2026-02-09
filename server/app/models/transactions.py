from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Date, ForeignKey, Boolean, Enum
from .base import Base, IDMixin
from datetime import date as DTdate
from app.utils.timezone import business_today
import enum

class TransactionType(str, enum.Enum):
    SALE = "sale"
    RETURN = "return"
    ADJUSTMENT = "adjustment"
    

class Transaction(IDMixin, Base):
    __tablename__ = "transactions"
    
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    
    posted_at: Mapped[DTdate] = mapped_column(Date, default=business_today, nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType, native_enum=False), default=TransactionType.SALE, nullable=False)
    subtotal: Mapped[int] = mapped_column(Integer, default=0)
    tax_total: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    is_posted: Mapped[bool] = mapped_column(Boolean, default=True)
    
    ticket = relationship("Ticket", back_populates="transactions", lazy="joined")
    line_items = relationship("LineItem", back_populates="transaction", cascade="all, delete-orphan", lazy="selectin")
    tenders = relationship("Tender", back_populates="transaction", cascade="all, delete-orphan", lazy="selectin")
    user = relationship("User", back_populates="transactions", lazy="selectin")
    location = relationship("Location", back_populates="transactions", lazy="selectin")

    
    # ---------------- Helpers ----------------
    def compute_total(self):
        """Compute snapshot totals from line items"""
        self.subtotal = sum(li.unit_price * li.quantity for li in self.line_items)
        self.tax_total = sum(li.tax_amount for li in self.line_items)
        self.total = sum(li.total for li in self.line_items)
    
    @property
    def total_paid(self):
        return sum(t.amount for t in self.tenders)
    
    @property
    def balance_delta(self):
        return self.total - self.total_paid
    
    
