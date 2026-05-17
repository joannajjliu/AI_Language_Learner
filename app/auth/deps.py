"""FastAPI dependencies for authenticated routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import Header, HTTPException, status

from app.auth.google import GoogleUser, verify_google_credential


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization must use Bearer scheme",
        )
    token = authorization[len(prefix) :].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    return token


def get_google_user_from_header(
    authorization: Annotated[str | None, Header()] = None,
) -> GoogleUser:
    """Require a valid Google ID token."""
    token = _extract_bearer_token(authorization)
    try:
        return verify_google_credential(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


def require_matching_user(
    payload_user_id: str,
    authorization: str | None,
) -> GoogleUser:
    """Verify the bearer token and ensure it matches the request user_id."""
    user = get_google_user_from_header(authorization)
    if payload_user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id does not match the signed-in Google account",
        )
    return user
