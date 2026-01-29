# app/models/line_item.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Boolean, ForeignKey, Numeric, String
from .base import Base
from decimal import Decimal, ROUND_HALF_UP

class LineItem(Base):
    __tablename__ = "line_items"
    
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("sales_categories.id"), nullable=False)
    
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    
    taxable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=True)
    tax_amount: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    
    is_return: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # ---------------- Relationships ----------------
    transaction = relationship("Transaction", back_populates="line_items", lazy="joined")
    category = relationship("SalesCategory", lazy="joined")
    allocations = relationship("LineItemTender", back_populates="line_item", cascade="all, delete-orphan")
    
    # ---------------- Helpers ----------------
    def compute_total(self):
        qty_price = self.unit_price * self.quantity
        tax_amt = Decimal(qty_price) * Decimal(self.tax_rate or 0)
        self.tax_amount = int(tax_amt.quantize(Decimal("1"), rounding=ROUND_HALF_UP)) if self.taxable else 0
        self.total = qty_price + self.tax_amount
        if self.is_return:
            self.total = -self.total
            
            
    @property
    def paid_total(self):
        return sum(t.applied_total for t in self.tenders)
    
    @property
    def remaining_total(self):
        return self.total - self.paid_total
    
    
