"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup: auto-create tables
    from .init_db import init_db
    await init_db()
    yield
    # Shutdown
    from .api.deps import engine
    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="芝士卷 Cheese Roll - AI 智能学习平台",
        description="Upload study materials, get AI-organized notes, flashcards, and practice questions",
        version="1.0.0",
        docs_url="/docs" if settings.APP_ENV == "development" else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    # CORS — allow Mini Program and Web origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict to specific domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router)

    # Health check
    @app.get("/health")
    async def health():
        return {"status": "ok", "env": settings.APP_ENV}

    return app


app = create_app()
