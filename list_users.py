import asyncio
from backend.database import db
from backend.models import UserInDB

async def list_users():
    db.connect()
    users = await db["users"].find().to_list(100)
    print(f"{'Email':<30} {'Role':<10} {'ID'}")
    print("-" * 60)
    for user in users:
        print(f"{user['email']:<30} {user.get('role', 'user'):<10} {user['_id']}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(list_users())
