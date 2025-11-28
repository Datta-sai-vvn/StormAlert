import os
import json
import redis
import asyncio
from backend.services.notifications import NotificationService
from backend.models import SettingsInDB

# Configure Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL)
QUEUE_NAME = "notifications"

notification_service = NotificationService()

async def process_task(task_data):
    try:
        settings = SettingsInDB(**task_data["settings"])
        message = task_data["message"]
        print(f"📨 Processing notification for {settings.user_id}")
        await notification_service.send_all(settings, message)
    except Exception as e:
        print(f"❌ Error processing task: {e}")

def run_worker():
    print(f"👷 Notification Worker Listening on {QUEUE_NAME}...")
    while True:
        # Blocking pop
        _, data = r.blpop(QUEUE_NAME)
        if data:
            task = json.loads(data)
            asyncio.run(process_task(task))

if __name__ == "__main__":
    run_worker()
