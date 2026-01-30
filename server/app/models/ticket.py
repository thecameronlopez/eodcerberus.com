from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Boolean, Date, ForeignKey, BigInteger, event
from .base import Base, IDMixin
from datetime import date as DTdate

class Ticket(IDMixin, Base):
    __tablename__ = "tickets"
    
    # ------------------- Core fields -------------------
    ticket_number: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    ticket_date: Mapped[DTdate] = mapped_column(Date, default=DTdate.today)
    
    
    # ------------------- Relationships -------------------
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    location = relationship("Location", lazy="selectin")
    transactions = relationship(
        "Transaction",
        back_populates="ticket",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tickets", lazy="selectin")
    
    sales_day_id: Mapped[int] = mapped_column(ForeignKey("sales_days.id"), nullable=False, index=True)
    sales_day = relationship("SalesDay", back_populates="tickets")
    
    
    # ------------------- Cached Totals -------------------
    subtotal: Mapped[int] = mapped_column(Integer, default=0)
    tax_total: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    
    
    # ------------------- Properties -------------------
    @property
    def total_paid(self) -> int:
        """ Sum of all tender amounts for this ticket """
        return sum(
            t.amount
            for tx in self.transactions
            for t in tx.tenders 
        )
    
    @property
    def balance_owed(self) -> int:
        """ How much is still owed on this ticket """
        return self.total - self.total_paid
    
    @property
    def is_open(self) -> bool:
        """ True if ticket is underpaid (layaway or partial payment) """
        return self.balance_owed > 0
    
    
    # ------------------- Methods ------------------- 
    def compute_total(self):
        """  
        Computes ticket subtotal, tax total, and total from child transactions.
        Should be ran whenever a transaction changes.
        """
        self.subtotal = sum(tx.subtotal for tx in self.transactions)
        self.tax_total = sum(tx.tax_total for tx in self.transactions)
        self.total = sum(tx.total for tx in self.transactions)

    

    
    
