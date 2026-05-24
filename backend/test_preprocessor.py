import asyncio
from database import AsyncSessionLocal
from services_v2.preprocessor import PreprocessorService
import os

async def test():
    async with AsyncSessionLocal() as session:
        file_path = os.path.join(os.getcwd(), "uploads", "threat_sample.log")
        if not os.path.exists(file_path):
             # Try one level up if not in backend/uploads
             file_path = os.path.join(os.path.dirname(os.getcwd()), "threat_sample.log")
        print(f"Processing {file_path}...")
        signals, stats = await PreprocessorService.process_file(file_path, session)
        print(f"Done. Signals: {len(signals)}, Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test())
