"""Entry, version, diff, comment, and conflict API schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EntryType
from app.schemas.collaboration import MentionOut


class EntryCreate(BaseModel):
    content: str = Field(min_length=1)
    entry_type: EntryType

    model_config = ConfigDict(extra="ignore")


class EntryUpdate(BaseModel):
    expected_version: int = Field(ge=1)
    new_content: str = Field(min_length=1)

    model_config = ConfigDict(extra="ignore")


class RevertRequest(BaseModel):
    target_version: int = Field(ge=1)
    expected_current_version: int = Field(ge=1)

    model_config = ConfigDict(extra="ignore")


class InternalEntryOut(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    entry_type: EntryType
    owner_role: str
    visibility: str
    created_by_user_id: str | None
    current_version: int
    content: str
    occurred_at: datetime
    source_kind: str
    source_reference: str | None
    created_at: datetime
    updated_at: datetime


class PatientEntryOut(BaseModel):
    id: str
    patient_id: str
    entry_type: EntryType
    content: str
    current_version: int
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entry_id: str
    version_number: int
    content: str
    created_by_user_id: str | None
    created_by_role: str
    base_version: int
    reverted_from_version: int | None
    created_at: datetime


class DiffOut(BaseModel):
    entry_id: str
    from_version: int
    to_version: int
    from_content: str
    to_content: str
    changed: bool


class ConflictOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entry_id: str
    expected_version: int
    actual_version: int
    attempted_content: str
    status: str
    submitted_by_user_id: str
    created_at: datetime


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entry_id: str
    parent_comment_id: str | None
    author_user_id: str
    body: str
    is_resolved: bool
    resolved_at: datetime | None
    resolved_by_user_id: str | None
    created_at: datetime
    updated_at: datetime
    mentions: list[MentionOut] = Field(default_factory=list)


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=5000)
    parent_comment_id: str | None = None
    mentioned_user_ids: list[str] = Field(default_factory=list, max_length=20)

    model_config = ConfigDict(extra="ignore")


class CommentResolution(BaseModel):
    is_resolved: bool

    model_config = ConfigDict(extra="ignore")
