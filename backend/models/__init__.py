from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from typing import Optional, List, Annotated
from datetime import datetime
from enum import Enum

# Helper for ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class AlgoMode(str, Enum):
    TRAILING = "trailing"
    ROLLING = "rolling"
    BOTH = "both"

class Exchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"

# --- User Models ---
class UserBase(BaseModel):
    email: EmailStr
    role: str = "user"

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserResponse(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

# --- Stock Models ---
class StockBase(BaseModel):
    symbol: str
    exchange: Exchange = Exchange.NSE
    active: bool = True

class StockCreate(StockBase):
    pass

class StockInDB(StockBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    instrument_token: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AlertFrequency(str, Enum):
    ONCE = "once"
    RECURRING = "recurring"
    ON_REVERSAL = "reversal"

class DataSource(str, Enum):
    ZERODHA = "zerodha"
    NSE_POLLING = "nse_polling"

# --- Settings Models ---
class SettingsBase(BaseModel):
    timeframe_minutes: int = 10
    dip_threshold: float = 1.0  # %
    rise_threshold: float = 1.0 # %
    cooldown_minutes: int = 15
    algo_mode: AlgoMode = AlgoMode.BOTH
    
    # Advanced Settings
    alert_frequency: AlertFrequency = AlertFrequency.ONCE
    market_hours_only: bool = True
    auto_refresh_token: bool = True
    auto_reconnect_ws: bool = True
    data_source: DataSource = DataSource.ZERODHA
    
    # Notification preferences
    email_enabled: bool = False
    whatsapp_enabled: bool = False
    telegram_enabled: bool = False
    
    email_address: Optional[EmailStr] = None
    whatsapp_number: Optional[str] = None
    telegram_chat_id: Optional[str] = None

class SettingsInDB(SettingsBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# --- Alert Models ---
class AlertType(str, Enum):
    DIP = "DIP"
    SPIKE = "SPIKE"

class AlertLog(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    stock_symbol: str
    price: float
    change_percent: float
    alert_type: AlertType
    algo_mode: AlgoMode = AlgoMode.BOTH
    exchange: Exchange = Exchange.NSE
    cooldown_applied: bool = False
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message: str

# --- System Models ---
class SystemState(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    access_token: Optional[str] = None
    request_token: Optional[str] = None
    public_token: Optional[str] = None
    date_received: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    status: str = "OFFLINE" # ONLINE, OFFLINE

# --- Auth Models ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
