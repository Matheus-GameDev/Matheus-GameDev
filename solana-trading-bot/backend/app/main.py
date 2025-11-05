import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.database import create_db_and_tables
from app.api import api_router
from app.engine import SignalEngine
from app.api.signals import broadcast_signal

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize signal engine
signal_engine = SignalEngine()

# Initialize scheduler
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("Starting Solana Trading Bot API")
    
    # Create database tables
    create_db_and_tables()
    
    # Initialize default trading pairs
    from app.utils.init_pairs import initialize_trading_pairs
    initialize_trading_pairs()
    
    # Register signal callback for SSE broadcasting
    async def signal_callback(signals):
        for signal in signals:
            await broadcast_signal(signal)
    
    signal_engine.register_callback(signal_callback)
    
    # Schedule signal generation
    scheduler.add_job(
        signal_engine.run_signal_generation,
        'interval',
        seconds=settings.SIGNAL_CHECK_INTERVAL_SECONDS,
        id='signal_generation'
    )
    
    # Schedule cleanup of expired signals
    scheduler.add_job(
        signal_engine.cleanup_expired_signals,
        'interval',
        minutes=5,
        id='cleanup_signals'
    )
    
    scheduler.start()
    logger.info("Scheduler started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Solana Trading Bot API")
    scheduler.shutdown()


# Create FastAPI app
app = FastAPI(
    title="Solana Trading Bot API",
    description="Non-custodial automated trading bot for Solana using VWAPBandsScalp strategy",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Solana Trading Bot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "scheduler_running": scheduler.running
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development"
    )
