from kiteconnect import KiteTicker
import os
import logging
import asyncio
import random
from datetime import datetime
from typing import List, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TickerService:
    def __init__(self):
        self.api_key = os.getenv("KITE_API_KEY")
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.kws = None
        self.subscribed_tokens = set()
        self.on_ticks_callback = None
        self.mock_mode = False
        self.connection_manager = None
        self.loop = None # Store the main event loop
        
        # Dashboard Metrics
        self.metrics = {
            "avg_latency": 0,
            "uptime_start": datetime.now().isoformat(),
            "total_ticks": 0
        }
        self.logs = []
        self.price_history = {} # token -> list of {price, time}
        self.connected = False

    def log(self, message: str, level: str = "INFO"):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        self.logs.append(entry)
        if len(self.logs) > 100:
            self.logs.pop(0)
        print(f"[{level}] {message}")

    def set_manager(self, manager):
        self.connection_manager = manager
        # Capture the running loop here, as this is called from startup_event
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

    def start(self, on_ticks: Callable, access_token: str = None):
        self.on_ticks_callback = on_ticks
        
        if access_token:
            self.access_token = access_token
        
        if not self.api_key or not self.access_token:
            logger.warning("KiteTicker credentials missing. Waiting for Admin Token.")
            return

        try:
            self.kws = KiteTicker(self.api_key, self.access_token)
            self.kws.on_ticks = self.on_ticks
            self.kws.on_connect = self.on_connect
            self.kws.on_close = self.on_close
            self.kws.on_error = self.on_error
            self.kws.on_reconnect = self.on_reconnect
            logger.info("KiteTicker initialized")
            self.connect()
        except Exception as e:
            logger.error(f"Failed to initialize KiteTicker: {e}. System OFFLINE.")
            self.connected = False

    def process_ticks(self, ticks):
        """Common tick processing logic (History, Metrics)"""
        self.connected = True
        self.metrics["total_ticks"] += len(ticks)
        
        # Update History
        for tick in ticks:
            token = tick["instrument_token"]
            if token not in self.price_history:
                self.price_history[token] = []
            
            self.price_history[token].append({
                "price": tick["last_price"],
                "time": tick["timestamp"] if "timestamp" in tick else datetime.now().isoformat(),
                "change": tick.get("change", 0)
            })
            
            # Keep last 30 points for sparkline
            if len(self.price_history[token]) > 30:
                self.price_history[token].pop(0)

    async def broadcast_ticks(self, ticks):
        """Async broadcast method"""
        if self.connection_manager:
            try:
                # Standard Tick Update
                payload = {
                    "type": "TICK_UPDATE",
                    "data": ticks
                }
                await self.connection_manager.broadcast(payload)
                
                # Dashboard Stats Update
                dashboard_payload = {
                    "type": "DASHBOARD_UPDATE",
                    "stats": {
                        "active_stocks": len(self.subscribed_tokens),
                        "connected": self.connected,
                        "uptime": self.metrics["uptime_start"]
                    }
                }
                await self.connection_manager.broadcast(dashboard_payload)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")

    async def start_mock_ticker(self):
        # STRICT PRODUCTION CHECK
        if os.getenv("PRODUCTION_MODE", "false").lower() == "true":
            logger.critical("ATTEMPTED TO START MOCK TICKER IN PRODUCTION MODE! SHUTTING DOWN.")
            raise RuntimeError("Mock Ticker is NOT allowed in Production.")

        self.log("Mock Ticker Started", "INFO")
        self.connected = True
        
        while True:
            if not self.subscribed_tokens:
                await asyncio.sleep(1)
                continue
        #         
        #     ticks = []
        #     for token in self.subscribed_tokens:
        #         # Generate random movement
        #         change = random.uniform(-0.5, 0.5)
        #         price = 1000 + random.uniform(-10, 10) # Base price around 1000
        #         
        #         ticks.append({
        #             "instrument_token": token,
        #             "last_price": round(price, 2),
        #             "last_quantity": 10,
        #             "average_price": round(price, 2),
        #             "volume": 10000,
        #             "buy_quantity": 0,
        #             "sell_quantity": 0,
        #             "ohlc": {"open": 1000, "high": 1010, "low": 990, "close": 1000},
        #             "change": round(change, 2),
        #             "timestamp": datetime.now().isoformat()
        #         })
        #     
        #     # 1. Process Logic
        #     self.process_ticks(ticks)
        #     
        #     # 2. Broadcast (Directly await since we are in async loop)
        #     await self.broadcast_ticks(ticks)
        # 
        #     # 3. Callback (Async if possible, or sync)
        #     if self.on_ticks_callback:
        #         try:
        #             await self.on_ticks_callback(ticks)
        #         except Exception:
        #             pass
        #     
        #     await asyncio.sleep(1) # Tick every second

    def connect(self, background=True):
        if self.kws and not self.mock_mode:
            self.kws.connect(threaded=background)

    def on_ticks(self, ws, ticks):
        """Called by KiteTicker in a separate thread"""
        # DEBUG LOG
        if len(ticks) > 0:
            print(f"DEBUG: Received {len(ticks)} ticks. First: {ticks[0]['instrument_token']} -> {ticks[0]['last_price']}")

        # 1. Process Logic
        self.process_ticks(ticks)

        # 2. Broadcast (Schedule on main loop)
        if self.connection_manager and self.loop:
            asyncio.run_coroutine_threadsafe(self.broadcast_ticks(ticks), self.loop)
        else:
            print("DEBUG: Connection Manager or Loop not ready for broadcast")

        # 3. Callback (Schedule on main loop if it's async, or run if sync)
        # Assuming on_ticks_callback is async (alert engine)
        if self.on_ticks_callback and self.loop:
             asyncio.run_coroutine_threadsafe(self.on_ticks_callback(ticks), self.loop)

    def on_connect(self, ws, response):
        logger.info("KiteTicker connected")
        if self.subscribed_tokens:
            ws.subscribe(list(self.subscribed_tokens))
            ws.set_mode(ws.MODE_FULL, list(self.subscribed_tokens))

    def on_close(self, ws, code, reason):
        logger.error(f"KiteTicker closed: {code} - {reason}")

    def on_error(self, ws, code, reason):
        logger.error(f"KiteTicker error: {code} - {reason}")

    def on_reconnect(self, ws, attempts_count):
        logger.info(f"KiteTicker reconnecting: {attempts_count}")

    def subscribe(self, tokens: List[int]):
        self.subscribed_tokens.update(tokens)
        if self.kws and self.kws.is_connected() and not self.mock_mode:
            self.kws.subscribe(list(tokens))
            self.kws.set_mode(self.kws.MODE_FULL, list(tokens))

    def unsubscribe(self, tokens: List[int]):
        self.subscribed_tokens.difference_update(tokens)
        if self.kws and self.kws.is_connected() and not self.mock_mode:
            self.kws.unsubscribe(list(tokens))

    async def restart(self, access_token: str):
        logger.info("Restarting Ticker Service with new token...")
        if self.kws:
            try:
                self.kws.close()
            except:
                pass
        
        self.access_token = access_token
        self.mock_mode = False
        self.connected = False
        
        # Re-initialize and connect
        try:
            self.kws = KiteTicker(self.api_key, self.access_token)
            self.kws.on_ticks = self.on_ticks
            self.kws.on_connect = self.on_connect
            self.kws.on_close = self.on_close
            self.kws.on_error = self.on_error
            self.kws.on_reconnect = self.on_reconnect
            self.connect()
        except Exception as e:
            logger.error(f"Failed to restart KiteTicker: {e}")

ticker_service = TickerService()
