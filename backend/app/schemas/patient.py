"""Patient-safe and internal patient response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    clinic_id: str
    synthetic_display_name: str
    created_at: datetime
