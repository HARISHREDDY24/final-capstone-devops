from sqlalchemy import Column, DateTime, Integer, String, Text, func
from .database import Base

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), nullable=False, index=True)
    description = Column(Text, nullable=False, default="")
    requester = Column(String(120), nullable=False, default="Unknown")
    category = Column(String(60), nullable=False, default="General")
    priority = Column(String(20), nullable=False, default="Medium", index=True)
    status = Column(String(30), nullable=False, default="Open", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
