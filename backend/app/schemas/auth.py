"""Authentication request and response schemas."""

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1)


class MembershipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    clinic_id: str
    clinic_name: str
    role: str


class MeResponse(BaseModel):
    id: str
    email: str
    display_name: str
    memberships: list[MembershipOut]
    patient_ids: list[str]


class LoginResponse(BaseModel):
    user: MeResponse
