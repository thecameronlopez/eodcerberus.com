from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Date, ForeignKey, Numeric, event
from .base import Base
from datetime import date as DTdate

class Transaction(Base):
    __tablename__ = "transactions"
    
    # Relationships
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False)
    ticket = relationship("Ticket", back_populates="transactions", lazy="selectin")
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="transactions", lazy="selectin")
    
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    location = relationship("Location", back_populates="transactions", lazy="selectin")
    
    # Date of transaction
    posted_date: Mapped[DTdate] = mapped_column(Date, nullable=False)
    
    # Transaction Totals
    units: Mapped[int] = mapped_column(Integer, default=0) #how many line items
    subtotal: Mapped[int] = mapped_column(Integer, nullable=False, default=0) #before tax
    tax_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0) #after tax    
    
    # Children
    line_items = relationship(
        "LineItem",
        back_populates="transaction",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    # Compute totals based on line items
    def compute_total(self):
        self.units = len(self.line_items)
        
        self.subtotal = sum(
            (-li.unit_price if li.is_return else li.unit_price) or 0
            for li in self.line_items
        )
        
        self.tax_total = sum(
            (-li.tax_amount if li.is_return else li.tax_amount) or 0
            for li in self.line_items
        )
        
        self.total = sum(li.signed_total for  li in self.line_items)
    
    
    def serialize(self, include_relationships=False):
        data = super().serialize(include_relationships=include_relationships)
        
        data["units"] = self.units
        data["subtotal"] = self.subtotal
        data["tax_total"] = self.tax_total
        data["total"] = self.total 
        
        data["posted_date"] = self.posted_date.isoformat()
        
        if include_relationships:
            data["line_items"] = [li.serialize() for li in self.line_items]

        
        return data
    
    
