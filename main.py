"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router as api_router

app = FastAPI(title="AI Language Tutor Backend", version="0.1.0")
app.include_router(api_router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
