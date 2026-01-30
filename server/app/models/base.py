from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer

class Base(DeclarativeBase):
    pass
class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    