
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from database import engine, Base, DATABASE_URL
import models_v2  # Import all models so Base can find them

async def update_schema():
    print("Updating database schema...")
    
    # Extract base URL to connect to MySQL server (without database)
    db_name = DATABASE_URL.split('/')[-1].split('?')[0]
    base_url = DATABASE_URL.rsplit('/', 1)[0].split('?')[0] # approximate parsing
    
    # Actually, simpler to just strip the DB name if it's standard format
    # But for safety, let's just try to connect to 'mysql' system db first to create the target db
    # Construct a URL for the 'sys' or no DB context if possible, but SQLAlchemy usually needs a DB.
    # We'll parse the URL properly.
    
    from sqlalchemy.engine.url import make_url
    url = make_url(DATABASE_URL)
    db_name = url.database
    
    # Create engine for server connection (no DB selected or 'mysql' db)
    # We'll explicitly set database to None or 'mysql'
    server_url = url.set(database='mysql')
    
    server_engine = create_async_engine(server_url)
    
    async with server_engine.begin() as conn:
        print(f"Checking if database '{db_name}' exists...")
        await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
        print(f"Database '{db_name}' ensured.")
        
    await server_engine.dispose()
    
    # Now connect to the actual DB and create tables
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Schema update complete.")

if __name__ == "__main__":
    asyncio.run(update_schema())
