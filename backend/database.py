from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "stormalert")

settings = Settings()

class Database:
    client: AsyncIOMotorClient = None
    db = None

    def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.DB_NAME]
        print(f"Connected to MongoDB: {settings.DB_NAME}")

    def close(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

    def __getitem__(self, item):
        return self.db[item]

    async def create_indexes(self):
        if self.db is not None:
            # Stocks Indexes
            await self.db["stocks"].create_index("instrument_token")
            await self.db["stocks"].create_index("user_id")
            await self.db["stocks"].create_index("active")
            await self.db["stocks"].create_index("symbol") # Search
            # Unique constraint for User + Symbol
            await self.db["stocks"].create_index([("user_id", 1), ("symbol", 1)], unique=True)
            
            # Alerts Indexes
            await self.db["alerts"].create_index("timestamp")
            await self.db["alerts"].create_index("user_id")
            await self.db["alerts"].create_index("alert_type") # Filtering
            
            # System State
            await self.db["system_state"].create_index([("date_received", -1)])
            
            print("Database indexes created.")

db = Database()

async def get_database():
    return db.db
