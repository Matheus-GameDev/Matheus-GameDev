import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from sqlmodel import Session, select

from app.database import engine as db_engine
from app.models import TradingPair, User, Signal
from app.models.signal import SignalType, SignalStatus
from app.services import BirdeyeClient, JupiterClient
from app.strategy import VWAPBandsScalp
from app.config import settings

logger = logging.getLogger(__name__)


class SignalEngine:
    """Engine for generating trading signals"""
    
    def __init__(self):
        self.birdeye = BirdeyeClient()
        self.jupiter = JupiterClient()
        self.strategy = VWAPBandsScalp()
        self.signal_callbacks = []
    
    def register_callback(self, callback):
        """Register a callback to be called when new signals are generated"""
        self.signal_callbacks.append(callback)
    
    async def generate_signals_for_pair(
        self,
        pair: TradingPair,
        user: User
    ) -> List[Signal]:
        """Generate signals for a specific trading pair and user"""
        signals = []
        
        try:
            # Fetch OHLCV data
            df = await self.birdeye.get_ohlcv(
                token_address=pair.base_mint,
                timeframe=settings.CANDLE_TIMEFRAME,
                limit=settings.STARTUP_CANDLE_COUNT
            )
            
            if df is None or len(df) < 50:
                logger.warning(f"Insufficient data for {pair.symbol}")
                return signals
            
            # Generate signal using strategy
            strategy_signal = self.strategy.generate_signal(df)
            
            # Only create signal if strategy indicates entry
            if strategy_signal.signal_type:
                # Check if there's already a pending signal for this pair/user
                with Session(db_engine) as session:
                    existing = session.exec(
                        select(Signal).where(
                            Signal.user_id == user.id,
                            Signal.pair_id == pair.id,
                            Signal.status == SignalStatus.PENDING
                        )
                    ).first()
                    
                    if existing:
                        logger.info(f"Signal already exists for {pair.symbol}, skipping")
                        return signals
                    
                    # Calculate order size based on user risk settings
                    order_size_usd = min(
                        user.max_position_size_usd,
                        settings.MAX_TRADE_SIZE_USD
                    )
                    
                    # Create new signal
                    signal = Signal(
                        user_id=user.id,
                        pair_id=pair.id,
                        symbol=pair.symbol,
                        signal_type=SignalType(strategy_signal.signal_type),
                        status=SignalStatus.PENDING,
                        entry_price=strategy_signal.entry_price,
                        stop_loss=strategy_signal.stop_loss,
                        take_profit=strategy_signal.take_profit,
                        current_price=strategy_signal.entry_price,
                        vwap=strategy_signal.vwap,
                        upper_band=strategy_signal.upper_band,
                        lower_band=strategy_signal.lower_band,
                        atr=strategy_signal.atr,
                        rsi=strategy_signal.rsi,
                        order_size_usd=order_size_usd,
                        expires_at=datetime.utcnow() + timedelta(minutes=5)
                    )
                    
                    session.add(signal)
                    session.commit()
                    session.refresh(signal)
                    
                    signals.append(signal)
                    logger.info(
                        f"Generated {signal.signal_type} signal for {pair.symbol} "
                        f"at {signal.entry_price:.4f}"
                    )
        
        except Exception as e:
            logger.error(f"Error generating signal for {pair.symbol}: {e}")
        
        return signals
    
    async def run_signal_generation(self):
        """Run signal generation for all active pairs and users"""
        logger.info("Starting signal generation cycle")
        
        try:
            with Session(db_engine) as session:
                # Get all active users with bot enabled
                users = session.exec(
                    select(User).where(
                        User.is_active == True,
                        User.bot_enabled == True
                    )
                ).all()
                
                if not users:
                    logger.info("No active users with bot enabled")
                    return
                
                # Get all active trading pairs
                pairs = session.exec(
                    select(TradingPair).where(TradingPair.is_active == True)
                ).all()
                
                if not pairs:
                    logger.warning("No active trading pairs")
                    return
                
                logger.info(f"Generating signals for {len(users)} users and {len(pairs)} pairs")
                
                # Generate signals for each user/pair combination
                all_signals = []
                for user in users:
                    for pair in pairs:
                        signals = await self.generate_signals_for_pair(pair, user)
                        all_signals.extend(signals)
                
                # Notify callbacks about new signals
                if all_signals:
                    for callback in self.signal_callbacks:
                        try:
                            await callback(all_signals)
                        except Exception as e:
                            logger.error(f"Error in signal callback: {e}")
                
                logger.info(f"Signal generation complete. Generated {len(all_signals)} signals")
        
        except Exception as e:
            logger.error(f"Error in signal generation cycle: {e}")
    
    async def cleanup_expired_signals(self):
        """Remove expired signals"""
        try:
            with Session(db_engine) as session:
                expired = session.exec(
                    select(Signal).where(
                        Signal.status == SignalStatus.PENDING,
                        Signal.expires_at < datetime.utcnow()
                    )
                ).all()
                
                for signal in expired:
                    signal.status = SignalStatus.EXPIRED
                    session.add(signal)
                
                session.commit()
                
                if expired:
                    logger.info(f"Marked {len(expired)} signals as expired")
        
        except Exception as e:
            logger.error(f"Error cleaning up expired signals: {e}")
