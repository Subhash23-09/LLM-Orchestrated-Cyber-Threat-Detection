import asyncio
from database import engine, Base
import models_v2

async def init_db():
    async with engine.begin() as conn:
        # Import all models to ensure they are registered with Base
        print("Creating tables in MySQL...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
