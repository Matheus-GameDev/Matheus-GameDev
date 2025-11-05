from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from datetime import datetime

from app.database import get_session
from app.models.user import User
from app.auth import generate_nonce, verify_signature, create_access_token, get_current_user

router = APIRouter()


class NonceRequest(BaseModel):
    wallet_address: str


class NonceResponse(BaseModel):
    nonce: str
    message: str


class VerifyRequest(BaseModel):
    wallet_address: str
    signature: str
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserSettingsUpdate(BaseModel):
    bot_enabled: bool | None = None
    risk_per_trade: float | None = None
    max_position_size_usd: float | None = None


@router.post("/nonce", response_model=NonceResponse)
async def get_nonce(
    request: NonceRequest,
    session: Session = Depends(get_session)
):
    """Generate a nonce for SIWS authentication"""
    
    # Get or create user
    statement = select(User).where(User.wallet_address == request.wallet_address)
    user = session.exec(statement).first()
    
    if not user:
        user = User(wallet_address=request.wallet_address)
        session.add(user)
    
    # Generate and store nonce
    nonce = generate_nonce()
    user.nonce = nonce
    
    session.commit()
    
    # Create message to sign
    message = f"Sign this message to authenticate with Solana Trading Bot.\n\nNonce: {nonce}"
    
    return NonceResponse(nonce=nonce, message=message)


@router.post("/verify", response_model=TokenResponse)
async def verify_wallet(
    request: VerifyRequest,
    session: Session = Depends(get_session)
):
    """Verify wallet signature and issue JWT token"""
    
    # Get user
    statement = select(User).where(User.wallet_address == request.wallet_address)
    user = session.exec(statement).first()
    
    if not user or not user.nonce:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nonce not found. Please request a nonce first."
        )
    
    # Verify the signature
    is_valid = verify_signature(
        message=request.message,
        signature=request.signature,
        public_key=request.wallet_address
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Clear nonce (one-time use)
    user.nonce = None
    user.last_login = datetime.utcnow()
    session.commit()
    session.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.wallet_address})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "wallet_address": user.wallet_address,
            "bot_enabled": user.bot_enabled,
            "risk_per_trade": user.risk_per_trade,
            "max_position_size_usd": user.max_position_size_usd
        }
    )


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user info"""
    return {
        "id": current_user.id,
        "wallet_address": current_user.wallet_address,
        "bot_enabled": current_user.bot_enabled,
        "risk_per_trade": current_user.risk_per_trade,
        "max_position_size_usd": current_user.max_position_size_usd,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }


@router.put("/settings")
async def update_user_settings(
    settings: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update user settings"""
    
    if settings.bot_enabled is not None:
        current_user.bot_enabled = settings.bot_enabled
    
    if settings.risk_per_trade is not None:
        if settings.risk_per_trade < 0.1 or settings.risk_per_trade > 10.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Risk per trade must be between 0.1% and 10%"
            )
        current_user.risk_per_trade = settings.risk_per_trade
    
    if settings.max_position_size_usd is not None:
        if settings.max_position_size_usd < 10 or settings.max_position_size_usd > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Max position size must be between $10 and $10,000"
            )
        current_user.max_position_size_usd = settings.max_position_size_usd
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return {
        "message": "Settings updated successfully",
        "user": {
            "bot_enabled": current_user.bot_enabled,
            "risk_per_trade": current_user.risk_per_trade,
            "max_position_size_usd": current_user.max_position_size_usd
        }
    }
