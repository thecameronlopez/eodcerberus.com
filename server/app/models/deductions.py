from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Date, ForeignKey
from .base import Base
from datetime import date as DTdate

class Deduction(Base):
    __tablename__ = "deductions"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="deductions", lazy="selectin")
    
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(300), nullable=False)
    date: Mapped[DTdate] = mapped_column(Date, default=DTdate.today)
    
    