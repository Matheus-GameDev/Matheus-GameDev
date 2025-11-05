from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TradeStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class TradeType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


class Trade(SQLModel, table=True):
    __tablename__ = "trades"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    signal_id: Optional[int] = Field(foreign_key="signals.id")
    pair_id: int = Field(foreign_key="trading_pairs.id")
    
    symbol: str
    trade_type: TradeType
    status: TradeStatus = Field(default=TradeStatus.PENDING)
    
    # Trade details
    side: str  # "buy" or "sell"
    entry_price: float
    amount_in: float
    amount_out: Optional[float] = None
    
    # Execution
    transaction_signature: Optional[str] = None
    jupiter_route: Optional[str] = None  # JSON string
    slippage_bps: int = Field(default=50)
    
    # PnL tracking
    realized_pnl: Optional[float] = None
    fees_paid: Optional[float] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    
    # Error handling
    error_message: Optional[str] = None
