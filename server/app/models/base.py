from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import DateTime, func
from enum import Enum
from datetime import date, datetime

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    
    _serialize_exclude = []
    
    def serialize(self, include_relationships=False) -> dict:
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        
        data.pop("password_hash", None)
        
        if include_relationships:
            for rel in self.__mapper__.relationships:
                value = getattr(self, rel.key)
                if value is None:
                    data[rel.key] = None
                elif rel.uselist:
                    data[rel.key] = [i.serialize() for i in value]
                else:
                    data[rel.key] = value.serialize()
        
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
            elif isinstance(value, (date, datetime)):
                data[key] = value.isoformat()
                
        return data