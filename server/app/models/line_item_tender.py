from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Boolean, ForeignKey

class LineItemTender(Base):
    __tablename__ = "line_item_tenders"
    
    
    #-------------------------Relationships-----------------------------------
    line_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("line_items.id"), nullable=False)
    tender_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenders.id"), nullable=False)
    
    line_item = relationship("LineItem", back_populates="payments", lazy="selectin")
    tender = relationship("Tender", back_populates="allocations", lazy="selectin")
    
        
    #-------------------------Amount Allocated-----------------------------------
    applied_pretax: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    applied_tax: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    applied_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    
    #-------------------------Properties-----------------------------------
    @property
    def sign(self):
        """ Return -1 for return items, 1 for normal items """
        return -1 if self.line_item.is_return else 1
    
    
    #-------------------------Serialize-----------------------------------
    def serialize(self, include_relationships=False):
        return super().serialize(include_relationships=include_relationships)