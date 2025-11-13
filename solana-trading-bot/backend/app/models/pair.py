from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class TradingPair(SQLModel, table=True):
    __tablename__ = "trading_pairs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(unique=True, index=True)  # e.g., "SOL/USDC"
    base_token: str  # e.g., "SOL"
    quote_token: str = Field(default="USDC")
    base_mint: str  # Solana token mint address
    quote_mint: str  # USDC mint address
    is_active: bool = Field(default=True)
    min_order_size: float = Field(default=10.0)
    max_order_size: float = Field(default=1000.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
