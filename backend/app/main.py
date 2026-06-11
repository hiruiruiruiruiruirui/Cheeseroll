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

    # DB diagnostic
    @app.get("/db-check")
    async def db_check():
        try:
            from sqlalchemy.ext.asyncio import create_async_engine
            from sqlalchemy import text
            engine = create_async_engine(settings.db_url_with_ssl, echo=False)
            async with engine.connect() as conn:
                tables = (await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))).fetchall()
                await engine.dispose()
                return {"db_ok": True, "db_url": settings.DATABASE_URL[:30]+"...", "tables": [t[0] for t in tables]}
        except Exception as e:
            return {"db_ok": False, "error": str(e)}

    return app


app = create_app()
