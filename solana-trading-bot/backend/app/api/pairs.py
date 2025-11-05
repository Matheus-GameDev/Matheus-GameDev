from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel

from app.database import get_session
from app.models import TradingPair, User
from app.auth import get_current_user

router = APIRouter()


class PairResponse(BaseModel):
    id: int
    symbol: str
    base_token: str
    quote_token: str
    base_mint: str
    quote_mint: str
    is_active: bool
    min_order_size: float
    max_order_size: float


class PairUpdate(BaseModel):
    is_active: bool


@router.get("", response_model=List[PairResponse])
async def get_trading_pairs(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all trading pairs"""
    pairs = session.exec(select(TradingPair)).all()
    return pairs


@router.get("/{pair_id}", response_model=PairResponse)
async def get_trading_pair(
    pair_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific trading pair"""
    pair = session.get(TradingPair, pair_id)
    
    if not pair:
        raise HTTPException(status_code=404, detail="Trading pair not found")
    
    return pair


@router.put("/{pair_id}")
async def update_trading_pair(
    pair_id: int,
    update: PairUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update trading pair settings (enable/disable)"""
    pair = session.get(TradingPair, pair_id)
    
    if not pair:
        raise HTTPException(status_code=404, detail="Trading pair not found")
    
    pair.is_active = update.is_active
    session.add(pair)
    session.commit()
    session.refresh(pair)
    
    return {
        "message": f"Trading pair {pair.symbol} {'enabled' if pair.is_active else 'disabled'}",
        "pair": pair
    }
