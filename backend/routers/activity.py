from fastapi import APIRouter, Depends, HTTPException, Query
from backend.database import get_database
from backend.models import AlertLog, UserInDB
from backend.routers.auth import get_current_user
from typing import List, Optional
from datetime import datetime, timedelta
import csv
import io
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/activity", tags=["Activity"])

@router.get("/list", response_model=List[AlertLog])
async def list_activity(
    symbol: Optional[str] = None,
    alert_type: Optional[str] = None,
    days: Optional[int] = None,
    min_change: Optional[float] = None,
    limit: int = 50,
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    query = {"user_id": current_user.id}
    
    if symbol:
        query["stock_symbol"] = {"$regex": symbol, "$options": "i"}
    
    if alert_type:
        query["alert_type"] = alert_type
        
    if days:
        start_date = datetime.utcnow() - timedelta(days=days)
        query["timestamp"] = {"$gte": start_date}
        
    if min_change:
        query["change_percent"] = {"$gte": min_change} # Absolute value check might be needed in real app

    cursor = db["alerts"].find(query).sort("timestamp", -1).limit(limit)
    logs = await cursor.to_list(length=limit)
    return [AlertLog(**log) for log in logs]

@router.get("/stats")
async def get_activity_stats(
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    # Mock aggregation for now, replace with real pipeline
    total_alerts = await db["alerts"].count_documents({"user_id": current_user.id})
    
    # Simple aggregation for top stocks
    pipeline = [
        {"$match": {"user_id": current_user.id}},
        {"$group": {"_id": "$stock_symbol", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_stocks = await db["alerts"].aggregate(pipeline).to_list(length=5)
    
    return {
        "total_alerts": total_alerts,
        "top_stocks": [{"symbol": item["_id"], "count": item["count"]} for item in top_stocks]
    }

@router.get("/export")
async def export_activity(
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    cursor = db["alerts"].find({"user_id": current_user.id}).sort("timestamp", -1)
    logs = await cursor.to_list(length=1000)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Symbol", "Type", "Price", "Change %", "Message"])
    
    for log in logs:
        writer.writerow([
            log.get("timestamp"),
            log.get("stock_symbol"),
            log.get("alert_type"),
            log.get("price"),
            log.get("change_percent"),
            log.get("message")
        ])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=activity_logs.csv"}
    )

@router.delete("/{log_id}")
async def delete_log(
    log_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    # In real app, validate ObjectId
    result = await db["alerts"].delete_one({"_id": log_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Log not found")
    return {"status": "success"}
