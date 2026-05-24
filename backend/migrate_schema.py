import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Use synchronous URL for migration
ASYNC_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://root:password@localhost/acd_sdi")
SYNC_URL = ASYNC_URL.replace("mysql+aiomysql://", "mysql+pymysql://")

def migrate():
    print(f"Connecting to {SYNC_URL}...")
    try:
        engine = create_engine(SYNC_URL)
        with engine.connect() as conn:
            print("Checking for column 'raw_event_type' in 'security_signals'...")
            result = conn.execute(text("SHOW COLUMNS FROM security_signals LIKE 'raw_event_type'"))
            column_exists = result.fetchone()
            
            if not column_exists:
                print("Column 'raw_event_type' not found. Adding it now...")
                conn.execute(text("ALTER TABLE security_signals ADD COLUMN raw_event_type VARCHAR(100) DEFAULT NULL AFTER attack_type"))
                print("Column 'raw_event_type' added successfully.")
            else:
                print("Column 'raw_event_type' already exists.")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
