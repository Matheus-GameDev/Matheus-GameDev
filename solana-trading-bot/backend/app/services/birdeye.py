import httpx
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class BirdeyeClient:
    """Client for Birdeye API to fetch OHLCV data"""
    
    def __init__(self):
        self.base_url = settings.BIRDEYE_BASE_URL
        self.api_key = settings.BIRDEYE_API_KEY
        self.headers = {
            "X-API-KEY": self.api_key,
            "Accept": "application/json"
        }
    
    async def get_ohlcv(
        self,
        token_address: str,
        timeframe: str = "1m",
        limit: int = 200
    ) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data for a token
        
        Args:
            token_address: Solana token mint address
            timeframe: Candle timeframe (1m, 5m, 15m, 1H, 4H, 1D)
            limit: Number of candles to fetch
        
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            # Map timeframe to Birdeye format
            timeframe_map = {
                "1m": "1m",
                "5m": "5m",
                "15m": "15m",
                "1h": "1H",
                "4h": "4H",
                "1d": "1D"
            }
            
            birdeye_timeframe = timeframe_map.get(timeframe.lower(), "1m")
            
            # Calculate time range
            now = int(datetime.utcnow().timestamp())
            
            # Birdeye OHLCV endpoint
            url = f"{self.base_url}/defi/ohlcv"
            params = {
                "address": token_address,
                "type": birdeye_timeframe,
                "time_to": now,
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if not data.get("success") or not data.get("data", {}).get("items"):
                    logger.warning(f"No OHLCV data returned for {token_address}")
                    return None
                
                items = data["data"]["items"]
                
                # Convert to DataFrame
                df = pd.DataFrame(items)
                
                # Rename columns to standard format
                df = df.rename(columns={
                    "unixTime": "timestamp",
                    "o": "open",
                    "h": "high",
                    "l": "low",
                    "c": "close",
                    "v": "volume"
                })
                
                # Select and order columns
                df = df[["timestamp", "open", "high", "low", "close", "volume"]]
                
                # Convert timestamp to datetime
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
                
                # Sort by timestamp
                df = df.sort_values("timestamp").reset_index(drop=True)
                
                # Limit to requested number of candles
                df = df.tail(limit)
                
                logger.info(f"Fetched {len(df)} candles for {token_address}")
                return df
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching OHLCV for {token_address}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {token_address}: {e}")
            return None
    
    async def get_token_price(self, token_address: str) -> Optional[float]:
        """Get current token price in USD"""
        try:
            url = f"{self.base_url}/defi/price"
            params = {"address": token_address}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("success") and data.get("data"):
                    return float(data["data"].get("value", 0))
                
                return None
                
        except Exception as e:
            logger.error(f"Error fetching price for {token_address}: {e}")
            return None
    
    async def get_multiple_prices(self, token_addresses: List[str]) -> Dict[str, float]:
        """Get prices for multiple tokens"""
        prices = {}
        
        for address in token_addresses:
            price = await self.get_token_price(address)
            if price:
                prices[address] = price
        
        return prices
