from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Boolean, ForeignKey, Date, Numeric, String, event
from .base import Base
from .enums import SalesCategoryEnumSA, PaymentTypeEnumSA, ProductCategoryEnumSA, TaxabilitySourceEnumSA, ProductCategoryEnum, SalesCategoryEnum, PaymentTypeEnum, TaxabilitySourceEnum
from datetime import date as DTdate
from decimal import Decimal, ROUND_HALF_UP

class LineItem(Base):
    __tablename__ = "line_items"
    
    # ------------------ Relationships ------------------
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), nullable=False)
    transaction = relationship("Transaction", back_populates="line_items", lazy="selectin")
    payments = relationship(
        "LineItemTender",
        back_populates="line_item",
        cascade="all, delete-orphan",
        lazy="selectin",
        )
    
    
    
    # ------------------ Classification ------------------
    category: Mapped[SalesCategoryEnum] = mapped_column(SalesCategoryEnumSA, nullable=False)    
    
    
    # ------------------ Pricing (in cents) ------------------
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # ------------------ Tax determination ------------------
    taxable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    taxability_source: Mapped[TaxabilitySourceEnum] = mapped_column(TaxabilitySourceEnumSA, nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=True)
    
    # ------------------ Computed values (in cents) ------------------
    tax_amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # ------------------ Return flag ------------------
    is_return: Mapped[bool] = mapped_column(Boolean, default=False)
    
    
    
    
    # ------------------ Helpers ------------------
    @property
    def signed_total(self):
        """
        Returns negative total for returns, and positive total for sales.
        """
        total = self.total or 0
        return -total if self.is_return else total
    
    def compute_total(self):
        """ 
        Computes tax amount and total.
        Assumes unit_price, taxable, tax_rate are already set
        """
        unit_price = Decimal(self.unit_price or 0)
        tax_rate = Decimal(str(self.tax_rate or 0))
        
        if self.taxable:
            raw_tax = unit_price * tax_rate
            self.tax_amount = int(
                raw_tax.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            )
        else:
            self.tax_amount = 0
        
        self.total = int(unit_price) + self.tax_amount        
    
    
    ###
    def serialize(self, include_relationships=False):
        data = super().serialize(include_relationships=include_relationships)
        
        data["unit_price"] = self.unit_price 
        data["tax_amount"] = self.tax_amount
        data["total"] = self.total
        
        data["tax_rate"] = float(self.tax_rate) * 100 if self.tax_rate else None
        data["is_return"] = self.is_return
        data["sales_category"] = self.category.value
        data["taxability_source"] = self.taxability_source.value
        
        return data
    
    