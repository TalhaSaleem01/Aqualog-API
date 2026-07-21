from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .database import TASK_TYPES


# ---------------------------------------------------------------------
# Aquarium log entry schemas
# ---------------------------------------------------------------------
class EntryBase(BaseModel):
    tank_name: str = Field(..., min_length=1, max_length=50)
    task_type: str
    notes: Optional[str] = Field(default="", max_length=300)
    performed_at: str = Field(..., description="Date the task was performed, e.g. 2026-07-20")
    completed: bool = False

    @field_validator("task_type")
    @classmethod
    def validate_task_type(cls, v: str) -> str:
        if v not in TASK_TYPES:
            raise ValueError(f"task_type must be one of {sorted(TASK_TYPES)}")
        return v


class EntryCreate(EntryBase):
    pass


class EntryUpdate(BaseModel):
    """All fields optional — PUT applies only what's provided."""
    tank_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    task_type: Optional[str] = None
    notes: Optional[str] = Field(default=None, max_length=300)
    performed_at: Optional[str] = None
    completed: Optional[bool] = None

    @field_validator("task_type")
    @classmethod
    def validate_task_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in TASK_TYPES:
            raise ValueError(f"task_type must be one of {sorted(TASK_TYPES)}")
        return v


class EntryOut(EntryBase):
    id: int


# ---------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"