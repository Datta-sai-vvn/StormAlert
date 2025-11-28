from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from backend.routers.auth import get_current_admin
from backend.database import get_database
from backend.models import SystemState
from backend.services.ticker import ticker_service
from backend.services.kite_client import kite_client
from kiteconnect import KiteConnect
from datetime import datetime, timedelta
import os
import urllib.parse

router = APIRouter(prefix="/api/admin", tags=["Admin"])

class TokenSubmission(BaseModel):
    request_token_url: str

@router.post("/submit-request-token")
async def submit_request_token(submission: TokenSubmission, admin = Depends(get_current_admin), db = Depends(get_database)):
    # 1. Extract request_token from URL
    try:
        parsed = urllib.parse.urlparse(submission.request_token_url)
        qs = urllib.parse.parse_qs(parsed.query)
        request_token = qs.get("request_token", [None])[0]
        
        if not request_token:
             # Try to see if the user just pasted the token itself
            if len(submission.request_token_url) > 20 and "http" not in submission.request_token_url:
                request_token = submission.request_token_url
            else:
                raise ValueError("No request_token found in URL")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid URL format: {str(e)}")

    # 2. Exchange for Access Token
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    
    if not api_key or not api_secret:
        raise HTTPException(status_code=500, detail="Server misconfiguration: Missing Kite API credentials")

    try:
        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        public_token = data.get("public_token")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to verify token with Zerodha: {str(e)}")

    # 3. Store in DB
    # Invalidate old tokens
    await db["system_state"].update_many({}, {"$set": {"status": "OFFLINE"}})
    
    new_state = SystemState(
        access_token=access_token,
        request_token=request_token,
        public_token=public_token,
        date_received=datetime.utcnow(),
        expires_at=datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=0), # Expire at end of today (UTC)
        status="ONLINE"
    )
    
    await db["system_state"].insert_one(new_state.model_dump(by_alias=True, exclude={"id"}))

    # 4. Update Services
    # Update Kite Client
    kite_client.set_access_token(access_token)
    
    # Restart Ticker
    await ticker_service.restart(access_token)

    return {"success": True, "message": "System is now ONLINE"}

@router.get("/system-status")
async def get_system_status(db = Depends(get_database)):
    # Get latest state
    state = await db["system_state"].find_one(sort=[("date_received", -1)])
    
    if not state:
        return {"status": "OFFLINE", "reason": "No token found"}
    
    # Check expiration (simple check, can be more robust)
    if state["expires_at"] < datetime.utcnow():
        return {"status": "OFFLINE", "reason": "Token expired"}
        
    return {
        "status": state["status"],
        "date_received": state["date_received"],
        "expires_at": state["expires_at"]
    }

@router.get("/status-live")
async def get_live_status(db = Depends(get_database), admin = Depends(get_current_admin)):
    from backend.services.alert_engine import alert_engine
    
    # Get latest state for token expiry
    state = await db["system_state"].find_one(sort=[("date_received", -1)])
    expires_in = 0
    if state and state.get("expires_at"):
        delta = state["expires_at"] - datetime.utcnow()
        expires_in = int(delta.total_seconds() / 60) if delta.total_seconds() > 0 else 0

    # Calculate DB Latency (simple ping)
    start = datetime.utcnow()
    await db.command("ping")
    db_latency = int((datetime.utcnow() - start).total_seconds() * 1000)

    return {
        "ticker_online": ticker_service.connected,
        "ticks_last_5s": len(ticker_service.price_history) if ticker_service.price_history else 0, # Approximation or need real metric
        "alerts_today": 0, # Need to fetch from DB count for today
        "cpu_percent": 0, # Placeholder
        "memory_percent": 0, # Placeholder
        "websocket_reconnects": 0, # Placeholder
        "token_expires_in_minutes": expires_in,
        "db_latency_ms": db_latency,
        "version": "1.0.0"
    }
