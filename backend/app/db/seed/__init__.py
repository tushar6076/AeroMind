import asyncio
from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
import app.db.models  # noqa: F401
from app.db.seed.user import seed_users
from app.db.seed.ai_model import seed_ai_models


async def run_seeds() -> None:
    # 1. Create tables asynchronously
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Seed default data asynchronously
    async with AsyncSessionLocal() as db:
        try:
            print("Starting database seeding process...")
            await seed_users(db)
            await seed_ai_models(db)
            print("Database seeding completed successfully.")
        except Exception as e:
            await db.rollback()
            print(f"An error occurred during seeding: {e}")
            raise e


if __name__ == "__main__":
    asyncio.run(run_seeds())