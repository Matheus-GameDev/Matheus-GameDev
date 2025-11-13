from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    wallet_address: str = Field(unique=True, index=True)
    nonce: Optional[str] = None
    is_active: bool = Field(default=True)
    bot_enabled: bool = Field(default=False)
    risk_per_trade: float = Field(default=1.0)  # % of portfolio
    max_position_size_usd: float = Field(default=100.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
