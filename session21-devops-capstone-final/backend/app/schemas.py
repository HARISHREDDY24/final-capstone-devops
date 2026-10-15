from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

TaskStatus = Literal["Todo", "In Progress", "Done"]
TaskPriority = Literal["Low", "Medium", "High"]


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=3000)
    status: TaskStatus = "Todo"
    priority: TaskPriority = "Medium"
    assignee: str | None = Field(default=None, max_length=100)
    due_date: date | None = None


class TaskCreate(TaskBase):
    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be blank")
        return value


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=3000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee: str | None = Field(default=None, max_length=100)
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def title_cannot_be_null_or_blank(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            raise ValueError("Title cannot be null or blank")
        return value.strip()

    @field_validator("status", "priority")
    @classmethod
    def enum_fields_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("Status and priority cannot be null")
        return value


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class TaskStats(BaseModel):
    total: int
    todo: int
    in_progress: int
    completed: int
    overdue: int
