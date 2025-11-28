import asyncio
import sys
from backend.database import db

async def promote_user(email):
    db.connect()
    result = await db["users"].update_one({"email": email}, {"$set": {"role": "admin"}})
    if result.modified_count > 0:
        print(f"Successfully promoted {email} to admin.")
    else:
        print(f"User {email} not found or already admin.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python promote_user.py <email>")
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(promote_user(sys.argv[1]))
