from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Boolean, ForeignKey, Date, Numeric, String, event
from .base import Base
from .enums import SalesCategoryEnumSA, PaymentTypeEnumSA, ProductCategoryEnumSA, TaxabilitySourceEnumSA, ProductCategoryEnum, SalesCategoryEnum, PaymentTypeEnum, TaxabilitySourceEnum
from datetime import date as DTdate

class LineItem(Base):
    __tablename__ = "line_items"
    
    # Parent Transaction
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), nullable=False)
    transaction = relationship("Transaction", back_populates="line_items", lazy="selectin")
    
    # Classification
    category: Mapped[SalesCategoryEnum] = mapped_column(SalesCategoryEnumSA, nullable=False)
    payment_type: Mapped[PaymentTypeEnum] = mapped_column(PaymentTypeEnumSA, nullable=False)
    
    # Pricing (in cents)
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Tax determination
    taxable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    taxability_source: Mapped[TaxabilitySourceEnum] = mapped_column(TaxabilitySourceEnumSA, nullable=False)
    
    # Tax calculations
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 4), nullable=True)
    tax_amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Final Price (unit price + tax if taxable else unit_price)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Flag for returns
    is_return: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Compute transaction sum
    @property
    def signed_total(self):
        """
        Returns negative total for returns, and positive total for sales.
        """
        total = self.total or 0
        return -total if self.is_return else total
    
    # Compute the line item total
    def compute_total(self):
        """ 
        Computes tax amount and total.
        Assumes unit_price, taxable, tax_rate are already set
        """
        unit_price = self.unit_price or 0
        tax_rate = float(self.tax_rate or 0)
        
        self.tax_amount = round(unit_price * tax_rate) if self.taxable else 0
        self.total = unit_price + self.tax_amount        
    
    
    ###
    def serialize(self, include_relationships=False):
        data = super().serialize(include_relationships=include_relationships)
        
        data["unit_price"] = self.unit_price 
        data["tax_amount"] = self.tax_amount
        data["total"] = self.total
        
        data["tax_rate"] = float(self.tax_rate) * 100 if self.tax_rate else None
        data["is_return"] = self.is_return
        data["payment_type"] = self.payment_type
        data["category"] = self.category
        
        return data
    
    