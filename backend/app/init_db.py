"""Auto-create tables on first startup (for Railway)."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from .config import settings
from .models.base import Base
from .models import *  # Import all models

async def init_db():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed subscription plans
    async with engine.begin() as conn:
        existing = await conn.execute(text("SELECT COUNT(*) FROM subscription_plans"))
        if existing.scalar() == 0:
            await conn.execute(text("""
                INSERT INTO subscription_plans (plan_type, name, price_cents, duration_days, daily_quota, features) VALUES
                ('daily', '包天', 990, 1, 1, '["1 document processing", "1 PDF export"]'),
                ('monthly', '包月', 4900, 30, 10, '["Unlimited processing", "Unlimited exports", "Multi-format support"]'),
                ('quarterly', '包季度', 9900, 90, 10, '["Unlimited processing", "Unlimited exports", "Multi-format support", "Wrong-answer book", "Learning paths"]')
                ON CONFLICT (plan_type) DO NOTHING
            """))
    await engine.dispose()
