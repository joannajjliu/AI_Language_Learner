"""Google authentication routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.google import GoogleUser, verify_google_credential
from app.memory import get_memory_store

router = APIRouter(prefix="/auth", tags=["auth"])

_PROFILE_DEFAULT_LANGUAGE = "English"
_PROFILE_DEFAULT_LEVEL = "A1"


class GoogleAuthRequest(BaseModel):
    credential: str = Field(..., min_length=1, description="Google ID token from Sign-In")


class GoogleAuthResponse(BaseModel):
    user_id: str
    email: str
    name: str
    picture: str | None = None


def _to_response(user: GoogleUser) -> GoogleAuthResponse:
    return GoogleAuthResponse(
        user_id=user.user_id,
        email=user.email,
        name=user.display_name,
        picture=user.picture,
    )


def _persist_user_profile(user: GoogleUser) -> None:
    store = get_memory_store()
    store.ensure_user(
        user.user_id,
        email=user.email,
        display_name=user.display_name,
        native_language=_PROFILE_DEFAULT_LANGUAGE,
        target_language=_PROFILE_DEFAULT_LANGUAGE,
        cefr_level=_PROFILE_DEFAULT_LEVEL,
    )


@router.post("/google", response_model=GoogleAuthResponse)
def auth_google(payload: GoogleAuthRequest) -> GoogleAuthResponse:
    """Exchange a Google ID token for application user identity."""
    try:
        user = verify_google_credential(payload.credential)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    _persist_user_profile(user)
    return _to_response(user)
