from app.db.seed import run_seeds
import asyncio

if __name__ == "__main__":
    asyncio.run(run_seeds())