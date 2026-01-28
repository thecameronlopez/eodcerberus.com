from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Date, ForeignKey, Numeric, event
from .base import Base
from datetime import date as DTdate

class Transaction(Base):
    __tablename__ = "transactions"
    
    #-----------------------Relationships-------------------------
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False)
    ticket = relationship("Ticket", back_populates="transactions", lazy="selectin")
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="transactions", lazy="selectin")
    
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    location = relationship("Location", back_populates="transactions", lazy="selectin")
    
    #---------------------Transaction Date-----------------------
    posted_date: Mapped[DTdate] = mapped_column(Date, nullable=False, default=DTdate.today)
    
    #-------------------Transaction Totals (cents)--------------
    units: Mapped[int] = mapped_column(Integer, default=0) #how many line items
    subtotal: Mapped[int] = mapped_column(Integer, nullable=False, default=0) #before tax
    tax_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0) #after tax    
    
    #------------------------Children-------------------------------
    line_items = relationship(
        "LineItem",
        back_populates="transaction",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    tenders = relationship(
        "Tender",
        back_populates="transaction",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    

    
    
    #------------------------Helpers-------------------------------
    def compute_total(self):
        """ Compute subtotal, tax, and total from line items """
        self.units = len(self.line_items)
        
        self.subtotal = sum(
            (-li.unit_price if li.is_return else li.unit_price) or 0
            for li in self.line_items
        )
        
        self.tax_total = sum(
            (-li.tax_amount if li.is_return else li.tax_amount) or 0
            for li in self.line_items
        )
        
        self.total = sum(li.signed_total for li in self.line_items)
        
        total_paid = sum(t.amount for t in self.tenders or [])
        
        
    @property
    def total_paid(self) -> int:
        """ Sum of all tenders on this transaction """
        return sum(t.amount for t in self.tenders or [])
    
    @property
    def balance_delta(self) -> int:
        """ 
        How this transaction affects the ticket balance.
        Positive = customer owes more
        Negative = Customer overpaid /credit
        """
        
        return self.total - self.total_paid
    
    #------------------------Serialize-------------------------------
    def serialize(self, include_relationships=False):
        data = super().serialize(include_relationships=include_relationships)

        data.update({
            "units": self.units,
            "subtotal": self.subtotal,
            "tax_total": self.tax_total,
            "total": self.total,
            "posted_date": self.posted_date.isoformat(),
            "total_paid": self.total_paid,
            "balance_delta": self.balance_delta
        })

        if include_relationships:
            # Line items
            data["line_items"] = [li.serialize(include_relationships=True) for li in self.line_items]

            # Tenders
            data["tenders"] = [t.serialize(include_relationships=True) for t in self.tenders]

            # Line item allocations per tender
            allocations = []
            for lit in getattr(self, "line_item_tenders", []):
                allocations.append({
                    "line_item_id": lit.line_item_id,
                    "tender_id": lit.tender_id,
                    "applied_pretax": lit.applied_pretax,
                    "applied_tax": lit.applied_tax,
                    "applied_total": lit.applied_total
                })
            data["line_item_tenders"] = allocations

        return data

    
    
