from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import asyncio
import json

from app.database import get_session
from app.models import Signal, User
from app.models.signal import SignalStatus
from app.auth import get_current_user

router = APIRouter()


class SignalResponse(BaseModel):
    id: int
    symbol: str
    signal_type: str
    status: str
    entry_price: float
    stop_loss: float
    take_profit: float
    current_price: float
    vwap: float
    upper_band: float
    lower_band: float
    atr: float
    rsi: float
    order_size_usd: float | None
    created_at: str
    expires_at: str | None


class SignalAction(BaseModel):
    action: str  # "approve" or "reject"


@router.get("", response_model=List[SignalResponse])
async def get_signals(
    status: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get signals for the current user"""
    query = select(Signal).where(Signal.user_id == current_user.id)
    
    if status:
        try:
            signal_status = SignalStatus(status)
            query = query.where(Signal.status == signal_status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    signals = session.exec(query.order_by(Signal.created_at.desc())).all()
    
    return [
        SignalResponse(
            id=s.id,
            symbol=s.symbol,
            signal_type=s.signal_type.value,
            status=s.status.value,
            entry_price=s.entry_price,
            stop_loss=s.stop_loss,
            take_profit=s.take_profit,
            current_price=s.current_price,
            vwap=s.vwap,
            upper_band=s.upper_band,
            lower_band=s.lower_band,
            atr=s.atr,
            rsi=s.rsi,
            order_size_usd=s.order_size_usd,
            created_at=s.created_at.isoformat(),
            expires_at=s.expires_at.isoformat() if s.expires_at else None
        )
        for s in signals
    ]


@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal(
    signal_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific signal"""
    signal = session.get(Signal, signal_id)
    
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    if signal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return SignalResponse(
        id=signal.id,
        symbol=signal.symbol,
        signal_type=signal.signal_type.value,
        status=signal.status.value,
        entry_price=signal.entry_price,
        stop_loss=signal.stop_loss,
        take_profit=signal.take_profit,
        current_price=signal.current_price,
        vwap=signal.vwap,
        upper_band=signal.upper_band,
        lower_band=signal.lower_band,
        atr=signal.atr,
        rsi=signal.rsi,
        order_size_usd=signal.order_size_usd,
        created_at=signal.created_at.isoformat(),
        expires_at=signal.expires_at.isoformat() if signal.expires_at else None
    )


@router.post("/{signal_id}/action")
async def signal_action(
    signal_id: int,
    action: SignalAction,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Approve or reject a signal"""
    signal = session.get(Signal, signal_id)
    
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    if signal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if signal.status != SignalStatus.PENDING:
        raise HTTPException(status_code=400, detail="Signal is not pending")
    
    if action.action == "approve":
        signal.status = SignalStatus.APPROVED
        message = "Signal approved"
    elif action.action == "reject":
        signal.status = SignalStatus.REJECTED
        message = "Signal rejected"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    session.add(signal)
    session.commit()
    session.refresh(signal)
    
    return {"message": message, "signal_id": signal.id, "status": signal.status.value}


# Store for SSE connections
signal_queues = {}


@router.get("/stream/events")
async def stream_signals(
    current_user: User = Depends(get_current_user)
):
    """Stream signals via Server-Sent Events"""
    
    async def event_generator():
        # Create a queue for this user
        queue = asyncio.Queue()
        signal_queues[current_user.id] = queue
        
        try:
            # Send initial connection message
            yield {
                "event": "connected",
                "data": json.dumps({"message": "Connected to signal stream"})
            }
            
            # Stream signals
            while True:
                signal_data = await queue.get()
                yield {
                    "event": "signal",
                    "data": json.dumps(signal_data)
                }
        except asyncio.CancelledError:
            # Clean up when client disconnects
            if current_user.id in signal_queues:
                del signal_queues[current_user.id]
            raise
    
    return EventSourceResponse(event_generator())


async def broadcast_signal(signal: Signal):
    """Broadcast a signal to the user's SSE connection"""
    if signal.user_id in signal_queues:
        signal_data = {
            "id": signal.id,
            "symbol": signal.symbol,
            "signal_type": signal.signal_type.value,
            "entry_price": signal.entry_price,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "rsi": signal.rsi,
            "order_size_usd": signal.order_size_usd
        }
        await signal_queues[signal.user_id].put(signal_data)
