
import asyncio
from sqlalchemy import text
from database import engine
from models_v2 import SecuritySignal, IncidentMemory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

async def clear_tables():
    async with engine.begin() as conn:
        print("Clearing tables...")
        await conn.execute(text("DELETE FROM security_signals"))
        await conn.execute(text("DELETE FROM incident_memory"))
        print("Tables cleared successfully.")

if __name__ == "__main__":
    try:
        asyncio.run(clear_tables())
    except RuntimeError as e:
        if "Event loop is closed" not in str(e):
            raise e
