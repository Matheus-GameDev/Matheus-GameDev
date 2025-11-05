from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class SignalType(str, Enum):
    LONG = "long"
    SHORT = "short"


class SignalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    EXPIRED = "expired"


class Signal(SQLModel, table=True):
    __tablename__ = "signals"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    pair_id: int = Field(foreign_key="trading_pairs.id")
    symbol: str
    signal_type: SignalType
    status: SignalStatus = Field(default=SignalStatus.PENDING)
    
    # Price levels
    entry_price: float
    stop_loss: float
    take_profit: float
    current_price: float
    
    # Technical indicators
    vwap: float
    upper_band: float
    lower_band: float
    atr: float
    rsi: float
    
    # Order details
    order_size_usd: Optional[float] = None
    order_size_tokens: Optional[float] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
