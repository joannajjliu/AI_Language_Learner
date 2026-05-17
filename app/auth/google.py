"""Verify Google Sign-In ID tokens."""

from __future__ import annotations

from dataclasses import dataclass

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.config import get_google_client_id


@dataclass(frozen=True)
class GoogleUser:
    """Authenticated Google account."""

    user_id: str
    email: str
    name: str
    picture: str | None


def google_user_id(google_sub: str) -> str:
    """Stable application user id for a Google account subject."""
    return f"google-{google_sub}"


def verify_google_credential(credential: str) -> GoogleUser:
    """Validate a Google ID token and return the signed-in user."""
    client_id = get_google_client_id()
    if not client_id:
        raise ValueError("Google sign-in is not configured on the server")

    try:
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            client_id,
        )
    except ValueError as exc:
        raise ValueError("Invalid or expired Google credential") from exc

    sub = str(idinfo.get("sub") or "").strip()
    if not sub:
        raise ValueError("Google credential is missing subject")

    email = str(idinfo.get("email") or "").strip()
    name = str(idinfo.get("name") or email or "Learner").strip()
    picture = idinfo.get("picture")
    picture_str = str(picture).strip() if picture else None

    return GoogleUser(
        user_id=google_user_id(sub),
        email=email,
        name=name,
        picture=picture_str,
    )
