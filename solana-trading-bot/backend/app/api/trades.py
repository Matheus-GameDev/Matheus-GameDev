from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_session
from app.models import Trade, Signal, User, TradingPair
from app.models.trade import TradeStatus, TradeType
from app.models.signal import SignalStatus
from app.services import JupiterClient
from app.auth import get_current_user
from app.config import settings

router = APIRouter()
jupiter_client = JupiterClient()


class QuoteRequest(BaseModel):
    input_mint: str
    output_mint: str
    amount: int
    slippage_bps: int = 50


class QuoteResponse(BaseModel):
    quote: dict
    input_amount: str
    output_amount: str
    price_impact_pct: str
    route_plan: list


class BuildTransactionRequest(BaseModel):
    signal_id: int
    quote: dict


class BuildTransactionResponse(BaseModel):
    transaction: str  # Base64 encoded transaction
    trade_id: int


class ConfirmTransactionRequest(BaseModel):
    trade_id: int
    signature: str


class TradeResponse(BaseModel):
    id: int
    symbol: str
    trade_type: str
    status: str
    side: str
    entry_price: float
    amount_in: float
    amount_out: float | None
    transaction_signature: str | None
    realized_pnl: float | None
    fees_paid: float | None
    created_at: str
    confirmed_at: str | None


@router.post("/quote", response_model=QuoteResponse)
async def get_swap_quote(
    request: QuoteRequest,
    current_user: User = Depends(get_current_user)
):
    """Get a swap quote from Jupiter"""
    
    quote = await jupiter_client.get_quote(
        input_mint=request.input_mint,
        output_mint=request.output_mint,
        amount=request.amount,
        slippage_bps=request.slippage_bps
    )
    
    if not quote:
        raise HTTPException(status_code=500, detail="Failed to get quote from Jupiter")
    
    return QuoteResponse(
        quote=quote,
        input_amount=quote.get("inAmount", "0"),
        output_amount=quote.get("outAmount", "0"),
        price_impact_pct=quote.get("priceImpactPct", "0"),
        route_plan=quote.get("routePlan", [])
    )


@router.post("/build", response_model=BuildTransactionResponse)
async def build_swap_transaction(
    request: BuildTransactionRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Build a swap transaction from an approved signal"""
    
    # Get and validate signal
    signal = session.get(Signal, request.signal_id)
    
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    if signal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if signal.status != SignalStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Signal must be approved first")
    
    # Get trading pair
    pair = session.get(TradingPair, signal.pair_id)
    
    if not pair:
        raise HTTPException(status_code=404, detail="Trading pair not found")
    
    # Build transaction via Jupiter
    swap_data = await jupiter_client.get_swap_transaction(
        quote=request.quote,
        user_public_key=current_user.wallet_address,
        wrap_unwrap_sol=True
    )
    
    if not swap_data or "swapTransaction" not in swap_data:
        raise HTTPException(status_code=500, detail="Failed to build swap transaction")
    
    # Create trade record
    trade = Trade(
        user_id=current_user.id,
        signal_id=signal.id,
        pair_id=pair.id,
        symbol=pair.symbol,
        trade_type=TradeType.MARKET,
        status=TradeStatus.PENDING,
        side="buy" if signal.signal_type.value == "long" else "sell",
        entry_price=signal.entry_price,
        amount_in=float(request.quote.get("inAmount", 0)) / 1e9,  # Convert from lamports
        jupiter_route=str(request.quote),
        slippage_bps=settings.DEFAULT_SLIPPAGE_BPS
    )
    
    session.add(trade)
    session.commit()
    session.refresh(trade)
    
    # Update signal status
    signal.status = SignalStatus.EXECUTED
    session.add(signal)
    session.commit()
    
    return BuildTransactionResponse(
        transaction=swap_data["swapTransaction"],
        trade_id=trade.id
    )


@router.post("/confirm")
async def confirm_transaction(
    request: ConfirmTransactionRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Confirm a transaction has been submitted"""
    
    trade = session.get(Trade, request.trade_id)
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    if trade.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update trade with transaction signature
    trade.transaction_signature = request.signature
    trade.status = TradeStatus.SUBMITTED
    trade.submitted_at = datetime.utcnow()
    
    session.add(trade)
    session.commit()
    session.refresh(trade)
    
    return {
        "message": "Transaction confirmed",
        "trade_id": trade.id,
        "signature": trade.transaction_signature
    }


@router.get("", response_model=List[TradeResponse])
async def get_trades(
    limit: int = 50,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get trade history for current user"""
    
    trades = session.exec(
        select(Trade)
        .where(Trade.user_id == current_user.id)
        .order_by(Trade.created_at.desc())
        .limit(limit)
    ).all()
    
    return [
        TradeResponse(
            id=t.id,
            symbol=t.symbol,
            trade_type=t.trade_type.value,
            status=t.status.value,
            side=t.side,
            entry_price=t.entry_price,
            amount_in=t.amount_in,
            amount_out=t.amount_out,
            transaction_signature=t.transaction_signature,
            realized_pnl=t.realized_pnl,
            fees_paid=t.fees_paid,
            created_at=t.created_at.isoformat(),
            confirmed_at=t.confirmed_at.isoformat() if t.confirmed_at else None
        )
        for t in trades
    ]


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific trade"""
    
    trade = session.get(Trade, trade_id)
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    if trade.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return TradeResponse(
        id=trade.id,
        symbol=trade.symbol,
        trade_type=trade.trade_type.value,
        status=trade.status.value,
        side=trade.side,
        entry_price=trade.entry_price,
        amount_in=trade.amount_in,
        amount_out=trade.amount_out,
        transaction_signature=trade.transaction_signature,
        realized_pnl=trade.realized_pnl,
        fees_paid=trade.fees_paid,
        created_at=trade.created_at.isoformat(),
        confirmed_at=trade.confirmed_at.isoformat() if trade.confirmed_at else None
    )
