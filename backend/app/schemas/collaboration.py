"""Schemas for safe clinic-scoped mentions and internal tasks."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TaskStatus


class MentionUserOut(BaseModel):
    user_id: str
    display_name: str
    role: str


class MentionOut(BaseModel):
    id: str
    mentioned_user_id: str
    display_name: str
    role: str
    created_at: datetime


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    assigned_to_user_id: str
    source_entry_id: str | None = None
    source_comment_id: str | None = None

    model_config = ConfigDict(extra="ignore")


class TaskUpdate(BaseModel):
    expected_version: int = Field(ge=1)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    assigned_to_user_id: str | None = None
    status: TaskStatus | None = None

    model_config = ConfigDict(extra="ignore")


class TaskOut(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    source_entry_id: str | None
    source_comment_id: str | None
    title: str
    created_by_user_id: str
    assigned_to: MentionUserOut
    status: TaskStatus
    version: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class TaskConflictOut(BaseModel):
    conflict_id: str
    expected_version: int
    actual_version: int
    message: str


class CollaborationResourceOut(BaseModel):
    resource_type: Literal["comment", "task"]
    resource_id: str
