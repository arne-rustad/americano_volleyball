"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import game_sessions

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Backend API for Americano Volleyball - Complex logic only",
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Americano Volleyball API",
        "version": settings.api_version,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check for monitoring."""
    return {"status": "healthy"}


# Only game session routes (complex logic)
app.include_router(
    game_sessions.router,
    prefix="/api",
    tags=["game_sessions"],
)

