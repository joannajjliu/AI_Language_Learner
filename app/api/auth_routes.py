"""Google authentication routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.google import GoogleUser, verify_google_credential
from app.config import is_google_auth_enabled

router = APIRouter(prefix="/auth", tags=["auth"])


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
        name=user.name,
        picture=user.picture,
    )


@router.post("/google", response_model=GoogleAuthResponse)
def auth_google(payload: GoogleAuthRequest) -> GoogleAuthResponse:
    """Exchange a Google ID token for application user identity."""
    if not is_google_auth_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Set GOOGLE_CLIENT_ID in the server environment to enable Google sign-in",
        )
    try:
        user = verify_google_credential(payload.credential)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    return _to_response(user)
