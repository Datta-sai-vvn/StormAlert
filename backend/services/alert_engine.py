import asyncio
from typing import Dict, List
from datetime import datetime, timedelta
from backend.services.algorithms import TrailingAlgo, RollingWindowAlgo
from backend.models import AlgoMode, AlertType, SettingsInDB
from backend.database import db

class AlertEngine:
    def __init__(self):
        self.trailing_algo = TrailingAlgo()
        self.rolling_algos: Dict[int, RollingWindowAlgo] = {} # user_id -> Algo
        self.user_settings: Dict[str, SettingsInDB] = {} # user_id -> Settings
        self.token_map: Dict[int, List[Tuple[str, str]]] = {} # token -> list of (user_id, symbol)
        self.last_alert_time: Dict[str, datetime] = {} # "user_id:token:type" -> timestamp
        self.connection_manager = None # WebSocket Manager

    def set_manager(self, manager):
        self.connection_manager = manager

    async def start(self):
        """Initialize cache and start background refresh task"""
        print("Starting Alert Engine...")
        self.queue = asyncio.Queue() # Initialize queue here to ensure loop exists
        self.alert_buffer = [] # Buffer for bulk inserts
        await self.refresh_cache()
        asyncio.create_task(self._cache_refresh_loop())
        asyncio.create_task(self._consume_ticks_loop())
        asyncio.create_task(self._cache_refresh_loop())
        asyncio.create_task(self._consume_ticks_loop())
        asyncio.create_task(self._flush_alerts_loop())
        asyncio.create_task(self._retention_policy_loop())

    async def _retention_policy_loop(self):
        """Delete alerts older than 30 days"""
        while True:
            try:
                cutoff = datetime.utcnow() - timedelta(days=30)
                result = await db["alerts"].delete_many({"timestamp": {"$lt": cutoff}})
                if result.deleted_count > 0:
                    print(f"Retention Policy: Deleted {result.deleted_count} old alerts.")
            except Exception as e:
                print(f"Error in retention loop: {e}")
            
            # Run once every 24 hours
            await asyncio.sleep(86400)

    async def _flush_alerts_loop(self):
        """Background task to flush alerts to DB in batches"""
        while True:
            await asyncio.sleep(1) # Flush every second
            if self.alert_buffer:
                to_insert = self.alert_buffer
                self.alert_buffer = [] # Clear buffer
                try:
                    await db["alerts"].insert_many(to_insert)
                    print(f"Flushed {len(to_insert)} alerts to DB")
                except Exception as e:
                    print(f"Error flushing alerts: {e}")
                    # Ideally, re-add to buffer or log to file
    
    async def enqueue_ticks(self, ticks: List[Dict]):
        """Put ticks into the queue (Non-blocking for Ticker)"""
        if hasattr(self, 'queue'):
            await self.queue.put(ticks)

    async def _consume_ticks_loop(self):
        """Consumer loop to process ticks from queue"""
        print("Alert Engine Consumer Loop Started")
        while True:
            try:
                ticks = await self.queue.get()
                await self.process_ticks(ticks)
                self.queue.task_done()
            except Exception as e:
                print(f"Error in alert consumer loop: {e}")

    async def _cache_refresh_loop(self):
        while True:
            await asyncio.sleep(60)
            try:
                await self.refresh_cache()
            except Exception as e:
                print(f"Error refreshing cache: {e}")

    async def refresh_cache(self):
        """Load all settings and active stocks into memory"""
        # 1. Load Settings
        settings_cursor = db["settings"].find({})
        new_settings = {}
        async for setting in settings_cursor:
            new_settings[str(setting["user_id"])] = SettingsInDB(**setting)
            # Initialize rolling algo if needed
            if str(setting["user_id"]) not in self.rolling_algos:
                self.rolling_algos[str(setting["user_id"])] = RollingWindowAlgo(window_minutes=setting["timeframe_minutes"])
        
        self.user_settings = new_settings

        # 2. Load Active Stocks & Build Token Map
        stocks_cursor = db["stocks"].find({"active": True})
        new_token_map = {}
        
        async for stock in stocks_cursor:
            tid = stock.get("instrument_token")
            if tid:
                if tid not in new_token_map:
                    new_token_map[tid] = []
                new_token_map[tid].append((str(stock["user_id"]), stock["symbol"]))
        
        self.token_map = new_token_map
        print(f"Cache Refreshed: {len(self.user_settings)} users, {len(self.token_map)} tokens monitored.")

    async def process_ticks(self, ticks: List[Dict]):
        # Optimized process_ticks using cached token_map
        
        for tick in ticks:
            token = tick["instrument_token"]
            price = tick["last_price"]
            
            # O(1) Lookup
            if token not in self.token_map:
                continue
                
            for user_id, symbol in self.token_map[token]:
                settings = self.user_settings.get(user_id)
                if not settings:
                    continue

                # --- Run Algorithms ---
                dip_pct, spike_pct = 0.0, 0.0
                
                # Trailing
                if settings.algo_mode in [AlgoMode.TRAILING, AlgoMode.BOTH]:
                    t_dip, t_spike = self.trailing_algo.process_tick(token, price)
                    dip_pct = max(dip_pct, t_dip or 0)
                    spike_pct = max(spike_pct, t_spike or 0)

                # Rolling
                if settings.algo_mode in [AlgoMode.ROLLING, AlgoMode.BOTH]:
                    r_algo = self.rolling_algos.get(user_id)
                    if r_algo:
                        r_dip, r_spike = r_algo.process_tick(token, price)
                        dip_pct = max(dip_pct, r_dip)
                        spike_pct = max(spike_pct, r_spike)

                # --- Check Thresholds ---
                if dip_pct >= settings.dip_threshold:
                    await self.trigger_alert(user_id, symbol, price, dip_pct, AlertType.DIP, settings)
                
                if spike_pct >= settings.rise_threshold:
                    await self.trigger_alert(user_id, symbol, price, spike_pct, AlertType.SPIKE, settings)

    async def trigger_alert(self, user_id: str, symbol: str, price: float, change: float, type: AlertType, settings: SettingsInDB):
        # Check Cooldown
        alert_key = f"{user_id}:{symbol}:{type}"
        last_time = self.last_alert_time.get(alert_key)
        
        if last_time and (datetime.utcnow() - last_time).total_seconds() < settings.cooldown_minutes * 60:
            return # In cooldown

        # Select emoji and phrase based on type
        if type == AlertType.DIP:
            emoji = "📉"
            action = "Price Dropped"
            phrase = "This stock has dropped significantly! Act accordingly."
        else: # Spike
            emoji = "📈"
            action = "Price Spiked"
            phrase = "Momentum is building up! Fast."

        formatted_message = (
            f"🚨 *StormAlert: {symbol}*\n"
            f"{emoji} *{action}:* {change:.2f}%\n"
            f"💰 *Current Price:* ₹{price:.2f}\n"
            f"_{phrase}_"
        )
        
        alert_log = {
            "user_id": user_id, 
            "stock_symbol": symbol,
            "price": price,
            "change_percent": change,
            "alert_type": type,
            "timestamp": datetime.utcnow(),
            "message": formatted_message
        }
        
        # Batch insert
        self.alert_buffer.append(alert_log)
        
        # Update cooldown
        self.last_alert_time[alert_key] = datetime.utcnow()
        
        # Send Notifications (Async)
        print(f"ALERT SENT: {alert_log['message']}")
        from backend.services.notifications import notification_service
        # Fire and forget to avoid blocking
        asyncio.create_task(notification_service.send_all(settings, alert_log['message']))

        # Broadcast to Frontend (Real-Time Activity Log)
        if self.connection_manager:
            try:
                # Convert datetime to string for JSON serialization
                log_payload = alert_log.copy()
                log_payload["timestamp"] = log_payload["timestamp"].isoformat()
                
                await self.connection_manager.broadcast({
                    "type": "ALERT_NEW",
                    "data": log_payload
                })
            except Exception as e:
                print(f"Error broadcasting alert: {e}")

alert_engine = AlertEngine()
