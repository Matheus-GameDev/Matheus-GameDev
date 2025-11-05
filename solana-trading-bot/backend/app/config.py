from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    
    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Database
    DATABASE_URL: str = "sqlite:///./trading_bot.db"
    
    # Solana
    SOLANA_RPC_URL: str
    SOLANA_NETWORK: str = "mainnet-beta"
    
    # Birdeye API
    BIRDEYE_API_KEY: str
    BIRDEYE_BASE_URL: str = "https://public-api.birdeye.so"
    
    # Jupiter API
    JUPITER_API_URL: str = "https://quote-api.jup.ag/v6"
    JUPITER_LIMIT_ORDER_URL: str = "https://api.jup.ag/limit/v2"
    
    # Trading
    DEFAULT_SLIPPAGE_BPS: int = 50
    MAX_TRADE_SIZE_USD: float = 1000.0
    MIN_TRADE_SIZE_USD: float = 10.0
    
    # Strategy
    SIGNAL_CHECK_INTERVAL_SECONDS: int = 60
    CANDLE_TIMEFRAME: str = "1m"
    STARTUP_CANDLE_COUNT: int = 200
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
