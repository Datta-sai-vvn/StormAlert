import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.services.db import db
from backend.routers import auth, stocks, settings, dashboard, websocket, activity, admin
from datetime import datetime
import asyncio

app = FastAPI()

# CORS Configuration
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(settings.router)
app.include_router(dashboard.router)
app.include_router(websocket.router)
app.include_router(activity.router)
app.include_router(admin.router)

@app.on_event("startup")
async def startup_db_client():
    print("="*50)
    print("🚀 StormAlert v1.0.0 - Production Mode") if os.getenv("PRODUCTION_MODE") == "true" else print("🔧 StormAlert v1.0.0 - Dev Mode")
    print("="*50)

    # Production Security Check
    if os.getenv("PRODUCTION_MODE", "false").lower() == "true":
        jwt_secret = os.getenv("JWT_SECRET")
        if not jwt_secret or jwt_secret == "super_secret_jwt_key_change_this":
            raise RuntimeError("CRITICAL SECURITY ERROR: Default JWT_SECRET used in PRODUCTION mode!")
            
    db.connect()
    await db.create_indexes()
    
    # Start Ticker Service (Real or Mock)
    from backend.services.ticker import ticker_service
    from backend.services.alert_engine import alert_engine
    from backend.routers.websocket import manager
    import asyncio
    
    # Initialize Alert Engine (Cache)
    await alert_engine.start()

    ticker_service.set_manager(manager)
    alert_engine.set_manager(manager)
    
    # Check for valid token in DB
    system_state = await db["system_state"].find_one(sort=[("date_received", -1)])
    access_token = None
    
    if system_state and system_state.get("status") == "ONLINE" and system_state.get("expires_at") > datetime.utcnow():
        access_token = system_state.get("access_token")
        print("Found valid access token in DB. Starting ONLINE.")
        
        # Update Kite Client
        from backend.services.kite_client import kite_client
        kite_client.set_access_token(access_token)
    else:
        print("No valid access token found. System starting OFFLINE.")
        # Ensure status is OFFLINE in DB if it was marked ONLINE but expired
        if system_state and system_state.get("status") == "ONLINE":
             await db["system_state"].update_one({"_id": system_state["_id"]}, {"$set": {"status": "OFFLINE"}})

    ticker_service.start(on_ticks=alert_engine.enqueue_ticks, access_token=access_token)
    
    # Cache Instruments
    from backend.services.kite_client import kite_client
    kite_client.fetch_instruments()
    
    # Subscribe to existing stocks
    try:
        stocks = await db["stocks"].find().to_list(1000)
        tokens = [s["instrument_token"] for s in stocks if "instrument_token" in s]
        if tokens:
            print(f"Subscribing to {len(tokens)} existing stocks...")
            ticker_service.subscribe(tokens)
    except Exception as e:
        print(f"Error subscribing to existing stocks: {e}")

    # Start Background Task for Token Expiration
    asyncio.create_task(check_token_expiration())

async def check_token_expiration():
    """Background task to check for token expiration every minute"""
    from backend.services.ticker import ticker_service
    while True:
        try:
            # Check every minute
            await asyncio.sleep(60)
            
            system_state = await db["system_state"].find_one(sort=[("date_received", -1)])
            
            if system_state and system_state.get("status") == "ONLINE":
                if system_state.get("expires_at") < datetime.utcnow():
                    print("Token expired! Switching system to OFFLINE.")
                    
                    # Update DB
                    await db["system_state"].update_one(
                        {"_id": system_state["_id"]}, 
                        {"$set": {"status": "OFFLINE"}}
                    )
                    
                    # Stop Ticker / Switch to Offline Mode
                    # We can't easily "stop" the ticker connection if it's blocking, 
                    # but we can set a flag or close the connection.
                    # TickerService.restart(None) effectively stops it if token is None/Invalid
                    await ticker_service.restart(None)
                    
        except Exception as e:
            print(f"Error in token expiration check: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    db.close()

@app.get("/")
async def root():
    return {"message": "StormAlert System is Running", "status": "active"}

@app.get("/api/status/live")
async def status():
    # Get real status from DB
    system_state = await db["system_state"].find_one(sort=[("date_received", -1)])
    status = "OFFLINE"
    if system_state:
        status = system_state.get("status", "OFFLINE")
        
    return {"status": status, "active_stocks": 0, "alerts_today": 0}

@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

@app.get("/metrics")
async def metrics():
    from backend.services.ticker import ticker_service
    from backend.services.alert_engine import alert_engine
    
    return {
        "ticker": {
            "connected": ticker_service.connected,
            "total_ticks": ticker_service.metrics["total_ticks"],
            "uptime": ticker_service.metrics["uptime_start"]
        },
        "alert_engine": {
            "monitored_users": len(alert_engine.user_settings),
            "monitored_tokens": len(alert_engine.token_map)
        },
        "system": {
            "cpu_usage": "Not implemented", # Requires psutil
            "memory_usage": "Not implemented"
        }
    }
