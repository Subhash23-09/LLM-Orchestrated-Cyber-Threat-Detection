
from database import SessionLocal, engine
from models_v2 import SecuritySignal, IncidentMemory
from sqlalchemy import text

def clear_tables():
    session = SessionLocal()
    try:
        print("Clearing tables...")
        session.query(SecuritySignal).delete()
        session.query(IncidentMemory).delete()
        session.commit()
        print("Tables cleared successfully.")
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    clear_tables()
