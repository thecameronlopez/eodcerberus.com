# app/models/line_item_tender.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey
from .base import Base

class LineItemTender(Base):
    __tablename__ = "line_item_tenders"
            
    line_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("line_items.id"), nullable=False, primary_key=True)
    tender_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenders.id"), nullable=False, primary_key=True)
    
    applied_pretax: Mapped[int] = mapped_column(Integer, default=0)
    applied_tax: Mapped[int] = mapped_column(Integer, default=0)
    applied_total: Mapped[int] = mapped_column(Integer, default=0)
    
    # ---------------- Relationships ----------------
    line_item = relationship("LineItem", back_populates="allocations", lazy="joined")
    tender = relationship("Tender", back_populates="allocations", lazy="joined")
    
  
