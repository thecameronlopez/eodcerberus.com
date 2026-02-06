from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, Enum, Index, Integer, func
from datetime import datetime, timezone
import enum

from .base import Base, IDMixin


class SalesDayStatus(str, enum.Enum):
    OPEN = "open"
    SUBMITTED = "submitted"
    LOCKED = "locked"


class SalesDay(IDMixin, Base):
    __tablename__ = "sales_days"
    __plural__ = "sales_days"

    # ------------------ Core fields ------------------
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False, index=True)

    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[SalesDayStatus] = mapped_column(
        Enum(SalesDayStatus, native_enum=False), default=SalesDayStatus.OPEN, nullable=False, index=True
    )

    starting_cash: Mapped[int] = mapped_column(Integer, nullable=False, default=50000)
    expected_cash: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_cash: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cash_difference: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ------------------ Relationships ------------------
    user = relationship("User", back_populates="sales_days")
    location = relationship("Location")

    tickets = relationship(
        "Ticket",
        back_populates="sales_day",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # ------------------ Indexes ------------------
    __table_args__ = (
        Index(
            "ix_one_open_day_per_user",
            "user_id",
            "status"
        ),
    )

    # ------------------ Computed methods ------------------
    def compute_expected_cash(self):
        """Sum starting cash + cash tenders across all tickets/transactions."""
        total_cash = sum(
            tender.amount
            for ticket in self.tickets
            for tx in ticket.transactions
            for tender in tx.tenders
            if tender.payment_type.name.upper() == "CASH"
        )
        self.expected_cash = self.starting_cash + total_cash
        return self.expected_cash

    def compute_cash_difference(self):
        if self.actual_cash is not None:
            if self.expected_cash is None:
                self.compute_expected_cash()
            self.cash_difference = self.actual_cash - self.expected_cash
        return self.cash_difference

    # ------------------ Convenience property ------------------
    @property
    def computed_expected_cash(self):
        return self.compute_expected_cash()

    @property
    def computed_cash_difference(self):
        return self.compute_cash_difference()
