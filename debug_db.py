import asyncio
from backend.database import db
from dotenv import load_dotenv
import os

load_dotenv()

async def test_db():
    print(f"Testing connection to: {os.getenv('MONGODB_URI')}")
    try:
        db.connect()
        print("Connection initialized.")
        
        # db.db is the AsyncIOMotorDatabase object
        collections = await db.db.list_collection_names()
        print(f"Collections: {collections}")
        
        # Try insert
        res = await db.db["debug"].insert_one({"test": "value"})
        print(f"Insert successful: {res.inserted_id}")
        
        # Clean up
        await db.db["debug"].delete_one({"_id": res.inserted_id})
        print("Cleanup successful.")
        
    except Exception as e:
        print(f"DB ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_db())
