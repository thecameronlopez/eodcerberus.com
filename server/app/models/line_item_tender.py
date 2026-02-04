# app/models/line_item_tender.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from .base import Base, IDMixin

class LineItemTender(IDMixin, Base):
    __tablename__ = "line_item_tenders"
    
    __table_args__ = (
        UniqueConstraint("line_item_id", "tender_id", name="uq_line_item_tender"),
    )
            
    line_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("line_items.id"), nullable=False)
    tender_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenders.id"), nullable=False)
    
    applied_pretax: Mapped[int] = mapped_column(Integer, default=0)
    applied_tax: Mapped[int] = mapped_column(Integer, default=0)
    applied_total: Mapped[int] = mapped_column(Integer, default=0)
    
    # ---------------- Relationships ----------------
    line_item = relationship("LineItem", back_populates="allocations", lazy="joined")
    tender = relationship("Tender", back_populates="allocations", lazy="joined")
    
  
