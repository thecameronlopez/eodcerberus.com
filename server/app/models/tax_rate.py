from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Date, ForeignKey, Numeric
from .base import Base, IDMixin

class TaxRate(IDMixin, Base):
    __tablename__ = "tax_rate"
    
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    effective_from: Mapped[Date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[Date] = mapped_column(Date, nullable=True)
    
    location = relationship("Location", back_populates="tax_rates")