from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Date, ForeignKey, BigInteger, event
from .base import Base
from datetime import date as DTdate

class Ticket(Base):
    __tablename__ = "tickets"
    
    ticket_number: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    ticket_date: Mapped[DTdate] = mapped_column(Date, default=DTdate.today)
    
    # Relationships
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    location = relationship("Location", lazy="selectin")
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tickets", lazy="selectin")
    
    # Ticket total derived from transaction totals
    subtotal: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tax_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Children
    transactions = relationship(
        "Transaction",
        back_populates="ticket",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    def compute_total(self):
        self.subtotal = sum(tx.subtotal for tx in self.transactions)
        self.tax_total = sum(tx.tax_total for tx in self.transactions)
        self.total = sum(tx.total for tx in self.transactions)
    
    def serialize(self, include_relationships=False):
        data = super().serialize(include_relationships=include_relationships)
        
        data["subtotal"] = self.subtotal
        data["tax_total"] = self.tax_total
        data["total"] = self.total
        
        if include_relationships:
            data["transactions"] = [t.serialize(include_relationships=include_relationships) for t in self.transactions]
            data["user"] = {
            "id": self.user.id,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
        }
            data["location"] = {
            "id": self.location.id,
            "name": self.location.name,
            "code": self.location.code
        }
        
        return data
    
