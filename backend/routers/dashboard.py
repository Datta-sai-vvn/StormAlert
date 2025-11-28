from fastapi import APIRouter, Depends
from backend.services.ticker import ticker_service
from backend.database import get_database
from datetime import datetime

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats():
    # Get stats from ticker service
    stats = {
        "active_stocks": len(ticker_service.subscribed_tokens),
        "alerts_today": 0, # TODO: Connect to alert engine
        "avg_latency": ticker_service.metrics.get("avg_latency", 0),
        "uptime": ticker_service.metrics.get("uptime_start", datetime.now().isoformat()),
        "connection_status": ticker_service.connected
    }
    return stats

@router.get("/logs")
async def get_system_logs(limit: int = 50):
    # In a real app, this would read from a log file or DB
    # For now, return mock logs or in-memory logs if we add them to ticker
    return ticker_service.logs[-limit:]

@router.get("/heatmap")
async def get_heatmap_data():
    # Return data for heatmap (symbol, % change)
    data = []
    for token, history in ticker_service.price_history.items():
        if history:
            last = history[-1]
            # We need symbol map, but for now let's just send token or enrich if possible
            # Ideally ticker service should map token -> symbol
            data.append({
                "token": token,
                "change": last.get("change", 0)
            })
    return data
