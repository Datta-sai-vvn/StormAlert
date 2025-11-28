import time
import requests
import logging
import json
import os
from datetime import datetime

# Configure Logging
logging.basicConfig(
    filename="watchdog.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Watchdog")

BASE_URL = os.getenv("BASE_URL", "http://localhost:8002")

def check_health():
    try:
        resp = requests.get(f"{BASE_URL}/healthz", timeout=5)
        if resp.status_code != 200:
            logger.error(f"Health Check Failed: {resp.status_code}")
            return False
        return True
    except Exception as e:
        logger.error(f"Health Check Error: {e}")
        return False

def check_metrics():
    try:
        resp = requests.get(f"{BASE_URL}/metrics", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            ticker = data.get("ticker", {})
            
            # Rule 1: Ticker Connected
            if not ticker.get("connected"):
                logger.warning("Ticker Service is DISCONNECTED")
            
            # Rule 2: Stale Ticks (Logic would need last_tick_time from metrics)
            # For now, just logging total ticks
            logger.info(f"Metrics: Ticks={ticker.get('total_ticks')}, Uptime={ticker.get('uptime')}")
            
            # Save snapshot
            with open("health.json", "w") as f:
                json.dump(data, f)
                
    except Exception as e:
        logger.error(f"Metrics Check Error: {e}")

def run_watchdog():
    logger.info("Watchdog Daemon Started")
    print("🐶 Watchdog Started. Monitoring system...")
    
    while True:
        is_healthy = check_health()
        if is_healthy:
            check_metrics()
        
        # Sleep 10 seconds
        time.sleep(10)

if __name__ == "__main__":
    run_watchdog()
