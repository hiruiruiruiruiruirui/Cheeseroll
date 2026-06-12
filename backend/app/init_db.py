"""Auto-create tables on first startup (for Railway)."""
import traceback
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from .config import settings
from .models.base import Base
from .models import *  # Import all models

async def init_db():
    engine = create_async_engine(settings.async_db_url, echo=True)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully")
    except Exception as e:
        print(f"Create tables error: {e}")
        traceback.print_exc()
    # Seed subscription plans
    try:
        async with engine.begin() as conn:
            r = await conn.execute(text("SELECT COUNT(*) FROM subscription_plans"))
            existing = r.scalar()
            print(f"Existing plans: {existing}")
            if existing == 0:
                for plan_type, name, price, days, quota, features in [
                    ('daily','包天',990,1,1,'["1 processing","1 PDF"]'),
                    ('monthly','包月',4900,30,10,'["Unlimited processing","Unlimited exports","Multi-format"]'),
                    ('quarterly','包季度',9900,90,10,'["Unlimited processing","Unlimited exports","Multi-format","Wrong-answer book","Learning paths"]'),
                ]:
                    await conn.execute(text("""
                        INSERT INTO subscription_plans (plan_type, name, price_cents, duration_days, daily_quota, features)
                        VALUES (:t, :n, :p, :d, :q, :f)
                    """), {"t": plan_type, "n": name, "p": price, "d": days, "q": quota, "f": features})
                print("Plans seeded")
    except Exception as e:
        print(f"Seed error: {e}")
        traceback.print_exc()
    await engine.dispose()
