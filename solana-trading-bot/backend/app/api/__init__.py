from fastapi import APIRouter
from .auth import router as auth_router
from .pairs import router as pairs_router
from .signals import router as signals_router
from .trades import router as trades_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(pairs_router, prefix="/pairs", tags=["pairs"])
api_router.include_router(signals_router, prefix="/signals", tags=["signals"])
api_router.include_router(trades_router, prefix="/trade", tags=["trades"])

__all__ = ["api_router"]
