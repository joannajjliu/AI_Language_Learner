"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth_routes import router as auth_router
from app.api.routes import router as api_router
from app.config import get_database_url
from app.db import ensure_schema
from app.memory import shutdown_memory_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_url = get_database_url()
    if database_url:
        ensure_schema(database_url)
    yield
    shutdown_memory_store()


app = FastAPI(
    title="AI Language Tutor Backend",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(api_router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
