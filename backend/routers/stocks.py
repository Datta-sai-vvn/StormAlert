from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from backend.database import get_database
from pydantic import BaseModel
from backend.models import StockCreate, StockInDB, UserInDB, StockBase
from backend.routers.auth import get_current_user
from bson import ObjectId

from backend.services.kite_client import kite_client

router = APIRouter(prefix="/api/stocks", tags=["Stocks"])

@router.get("/search")
async def search_stocks(query: str):
    return kite_client.search_instruments(query)

@router.get("/", response_model=List[StockInDB])
async def list_stocks(
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    stocks_cursor = db["stocks"].find({"user_id": current_user.id})
    stocks = await stocks_cursor.to_list(length=500)
    return stocks

@router.post("/add", response_model=StockInDB)
async def add_stock(
    stock: StockCreate,
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    # Validate with Kite Cache
    # We expect the frontend to send the correct symbol, but we should verify
    # and get the instrument_token if not provided (though frontend should ideally send it)
    
    # For now, we assume frontend sends just symbol, so we look it up
    instruments = kite_client.search_instruments(stock.symbol)
    # Exact match check
    valid_inst = next((i for i in instruments if i["tradingsymbol"] == stock.symbol), None)
    
    if not valid_inst:
        raise HTTPException(status_code=400, detail="Invalid stock symbol. Please select from search.")

    # Check if stock already exists for user
    existing_stock = await db["stocks"].find_one({
        "user_id": current_user.id,
        "symbol": stock.symbol
    })
    if existing_stock:
        raise HTTPException(status_code=400, detail="Stock already in watchlist")

    new_stock = StockInDB(
        user_id=current_user.id,
        symbol=valid_inst["tradingsymbol"],
        instrument_token=valid_inst["instrument_token"],
        exchange=valid_inst["exchange"]
    )
    
    result = await db["stocks"].insert_one(new_stock.model_dump(by_alias=True, exclude={"id"}))
    created_stock = await db["stocks"].find_one({"_id": result.inserted_id})
    
    # Subscribe in Ticker
    from backend.services.ticker import ticker_service
    ticker_service.subscribe([valid_inst["instrument_token"]])
    
    return StockInDB(**created_stock)

class BulkAddRequest(BaseModel):
    symbols: List[str]
    exchange: str = "NSE"

@router.post("/bulk-add")
async def bulk_add_stocks(
    request: BulkAddRequest,
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    added = []
    failed = []
    
    for symbol in request.symbols:
        symbol = symbol.upper()
        # Validate
        instruments = kite_client.search_instruments(symbol)
        valid_inst = next((i for i in instruments if i["tradingsymbol"] == symbol), None)
        
        if not valid_inst:
            failed.append({"symbol": symbol, "reason": "Invalid Symbol"})
            continue
            
        # Check duplicate
        exists = await db["stocks"].find_one({"user_id": current_user.id, "symbol": symbol})
        if exists:
            failed.append({"symbol": symbol, "reason": "Already in watchlist"})
            continue
            
        # Add
        new_stock = StockInDB(
            user_id=current_user.id,
            symbol=valid_inst["tradingsymbol"],
            instrument_token=valid_inst["instrument_token"],
            exchange=valid_inst["exchange"]
        )
        await db["stocks"].insert_one(new_stock.model_dump(by_alias=True, exclude={"id"}))
        added.append(symbol)
        
        # Subscribe
        from backend.services.ticker import ticker_service
        ticker_service.subscribe([valid_inst["instrument_token"]])
        
    return {"added": added, "failed": failed}

@router.delete("/{symbol}")
async def remove_stock(
    symbol: str,
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    result = await db["stocks"].delete_one({
        "user_id": current_user.id,
        "symbol": symbol
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Stock not found")
        
    return {"message": "Stock removed successfully"}
