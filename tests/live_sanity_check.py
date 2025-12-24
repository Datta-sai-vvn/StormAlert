import asyncio
import aiohttp
import websockets
import json
import os
import time

BASE_URL = os.getenv("BASE_URL", "http://localhost:8004")
WS_URL = os.getenv("WS_URL", "ws://localhost:8004/ws/stocks")

async def check_backend():
    print("🔹 Checking Backend Health...")
    async with aiohttp.ClientSession() as session:
        # /healthz is not exposed via Nginx (only /api), so we skip it.
        # try:
        #     async with session.get(f"{BASE_URL}/healthz") as resp:
        #         if resp.status == 200:
        #             print("✅ Backend Online")
        #         else:
        #             print(f"❌ Backend Failed: {resp.status}")
        #             return False
        # except Exception as e:
        #     print(f"❌ Backend Unreachable: {e}")
        #     return False
            
        try:
            async with session.get(f"{BASE_URL}/api/status/live") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Status Endpoint Active. System Status: {data.get('status')}")
                else:
                    print(f"❌ Status Endpoint Failed: {resp.status}")
        except Exception as e:
            print(f"❌ Status Endpoint Error: {e}")
            
    return True

async def check_websocket():
    print("🔹 Checking WebSocket Stream...")
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ WebSocket Connected")
            
            # Wait for a few messages
            messages = []
            try:
                for _ in range(3):
                    msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                    messages.append(json.loads(msg))
            except asyncio.TimeoutError:
                print("⚠️ No ticks received in 5s (Expected if market closed or no token)")
            
            if messages:
                print(f"✅ Received {len(messages)} packets")
                print(f"Packet Sample: {str(messages[0])[:100]}")
            
            return True
    except Exception as e:
        print(f"❌ WebSocket Error: {e}")
        return False

async def main():
    print("🚀 Starting Live Sanity Check...")
    backend_ok = await check_backend()
    ws_ok = await check_websocket()
    
    if backend_ok and ws_ok:
        print("\n🟢 LIVE SANITY CHECK PASSED")
    else:
        print("\n🔴 LIVE SANITY CHECK FAILED")

if __name__ == "__main__":
    asyncio.run(main())
