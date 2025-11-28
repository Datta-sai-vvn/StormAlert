import asyncio
import websockets
import logging
import json
import os
from datetime import datetime

# Configure Logging
logging.basicConfig(
    filename="shadow_log.jsonl",
    level=logging.INFO,
    format="%(message)s"
)
logger = logging.getLogger("ShadowLogger")

WS_URL = os.getenv("WS_URL", "ws://localhost:8002/ws/stocks")

async def shadow_log():
    print(f"🕵️ Shadow Logger connecting to {WS_URL}...")
    while True:
        try:
            async with websockets.connect(WS_URL) as websocket:
                print("✅ Shadow Logger Connected")
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    # Log everything
                    entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "type": data.get("type"),
                        "data_summary": str(data.get("data"))[:100] # Truncate for brevity
                    }
                    logger.info(json.dumps(entry))
                    
        except Exception as e:
            print(f"❌ Shadow Logger Error: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(shadow_log())
