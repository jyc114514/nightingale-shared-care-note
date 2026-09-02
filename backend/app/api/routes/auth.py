"""Cookie-backed authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_allowed_origin
from app.config import Settings, get_settings
from app.core.security import (
    SESSION_COOKIE,
    create_session_token,
    verify_password,
)
from app.db.session import get_db
from app.models import Clinic, ClinicMembership, PatientUserLink, User
from app.schemas.auth import LoginRequest, LoginResponse, MembershipOut, MeResponse


router = APIRouter(prefix="/auth", tags=["auth"])


def make_me_response(db: Session, user: User) -> MeResponse:
    membership_rows = db.execute(
        select(ClinicMembership, Clinic)
        .join(Clinic, Clinic.id == ClinicMembership.clinic_id)
        .where(ClinicMembership.user_id == user.id)
        .order_by(ClinicMembership.clinic_id)
    ).all()
    memberships = [
        MembershipOut(
            clinic_id=membership.clinic_id,
            clinic_name=clinic.name,
            role=str(getattr(membership.role, "value", membership.role)),
        )
        for membership, clinic in membership_rows
    ]
    patient_ids = list(
        db.scalars(
            select(PatientUserLink.patient_id)
            .where(PatientUserLink.user_id == user.id)
            .order_by(PatientUserLink.patient_id)
        )
    )
    return MeResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        memberships=memberships,
        patient_ids=patient_ids,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    dependencies=[Depends(require_allowed_origin)],
)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
    app_settings: Settings = Depends(get_settings),
) -> LoginResponse:
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email.lower()))
    if (
        user is None
        or not user.is_active
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    response.set_cookie(
        key=SESSION_COOKIE,
        value=create_session_token(user.id, app_settings),
        max_age=app_settings.session_ttl_minutes * 60,
        httponly=True,
        secure=app_settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    return LoginResponse(user=make_me_response(db, user))


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user), Depends(require_allowed_origin)],
)
def logout(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE, path="/")


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MeResponse:
    return make_me_response(db, user)
