from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Boolean, Date, ForeignKey, BigInteger, event
from .base import Base
from datetime import date as DTdate

class Ticket(Base):
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
    
    
    # ------------------- Cached Totals -------------------
    subtotal: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tax_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    open_balance: Mapped[bool] = mapped_column(Boolean, default=False)    
    
    
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
        self.open_balance = sum(t.amount for tx in self.transactions for t in tx.tenders) < self.total

    

    #----------------Serialize------------------
    def serialize(self, include_relationships=False):
        data = super().serialize(include_relationships=include_relationships)
        data.update({
            "subtotal": self.subtotal,
            "tax_total": self.tax_total,
            "total": self.total,
            "balance_owed": self.balance_owed,
            "open_balance": self.open_balance,
            "is_open": self.is_open
        })

        if include_relationships:
            data["transactions"] = [tx.serialize(include_relationships=True) for tx in self.transactions]
            data["user"] = {
                "id": self.user.id,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name
            }
            data["location"] = {
                "id": self.location.id,
                "name": self.location.name,
                "code": self.location.code
            }

        return data
    
