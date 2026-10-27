from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Priority = Literal["Low", "Medium", "High", "Urgent"]
Status = Literal["Open", "In Progress", "Resolved", "Closed"]

class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(default="", max_length=5000)
    requester: str = Field(default="Unknown", min_length=1, max_length=120)
    category: str = Field(default="General", max_length=60)
    priority: Priority = "Medium"
    status: Status = "Open"

class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=160)
    description: str | None = Field(default=None, max_length=5000)
    requester: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, max_length=60)
    priority: Priority | None = None
    status: Status | None = None

class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    requester: str
    category: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime
