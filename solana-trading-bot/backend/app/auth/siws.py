import secrets
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
import base58
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from app.config import settings
from app.database import get_session
from app.models.user import User

security = HTTPBearer()


def generate_nonce() -> str:
    """Generate a random nonce for SIWS authentication"""
    return secrets.token_urlsafe(32)


def verify_signature(message: str, signature: str, public_key: str) -> bool:
    """
    Verify a Solana wallet signature
    
    Args:
        message: The message that was signed
        signature: Base58 encoded signature
        public_key: Base58 encoded public key (wallet address)
    
    Returns:
        bool: True if signature is valid
    """
    try:
        # Decode the signature and public key from base58
        signature_bytes = base58.b58decode(signature)
        public_key_bytes = base58.b58decode(public_key)
        
        # Create a VerifyKey from the public key
        verify_key = VerifyKey(public_key_bytes)
        
        # Verify the signature
        verify_key.verify(message.encode('utf-8'), signature_bytes)
        return True
    except (BadSignatureError, Exception) as e:
        print(f"Signature verification failed: {e}")
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        wallet_address: str = payload.get("sub")
        
        if wallet_address is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    statement = select(User).where(User.wallet_address == wallet_address)
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user
