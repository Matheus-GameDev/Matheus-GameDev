import httpx
from typing import Dict, Optional, List
import logging
import json

from app.config import settings

logger = logging.getLogger(__name__)


class JupiterClient:
    """Client for Jupiter Aggregator API v6"""
    
    def __init__(self):
        self.quote_url = settings.JUPITER_API_URL
        self.limit_order_url = settings.JUPITER_LIMIT_ORDER_URL
    
    async def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = 50
    ) -> Optional[Dict]:
        """
        Get a swap quote from Jupiter
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount in smallest unit (lamports for SOL)
            slippage_bps: Slippage tolerance in basis points (50 = 0.5%)
        
        Returns:
            Quote data including routes and price impact
        """
        try:
            url = f"{self.quote_url}/quote"
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": slippage_bps,
                "onlyDirectRoutes": False,
                "asLegacyTransaction": False
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                quote = response.json()
                logger.info(f"Got Jupiter quote: {amount} {input_mint[:8]}... -> {output_mint[:8]}...")
                return quote
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting Jupiter quote: {e}")
            logger.error(f"Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            return None
        except Exception as e:
            logger.error(f"Error getting Jupiter quote: {e}")
            return None
    
    async def get_swap_transaction(
        self,
        quote: Dict,
        user_public_key: str,
        wrap_unwrap_sol: bool = True,
        fee_account: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get a serialized swap transaction from Jupiter
        
        Args:
            quote: Quote data from get_quote()
            user_public_key: User's wallet public key
            wrap_unwrap_sol: Whether to wrap/unwrap SOL automatically
            fee_account: Optional fee account for referral fees
        
        Returns:
            Transaction data with swapTransaction (base64 encoded)
        """
        try:
            url = f"{self.quote_url}/swap"
            
            payload = {
                "quoteResponse": quote,
                "userPublicKey": user_public_key,
                "wrapAndUnwrapSol": wrap_unwrap_sol,
                "dynamicComputeUnitLimit": True,
                "prioritizationFeeLamports": "auto"
            }
            
            if fee_account:
                payload["feeAccount"] = fee_account
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                swap_data = response.json()
                logger.info(f"Got Jupiter swap transaction for user {user_public_key[:8]}...")
                return swap_data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting swap transaction: {e}")
            logger.error(f"Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            return None
        except Exception as e:
            logger.error(f"Error getting swap transaction: {e}")
            return None
    
    async def get_token_list(self) -> Optional[List[Dict]]:
        """Get list of all tokens supported by Jupiter"""
        try:
            url = "https://token.jup.ag/all"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                tokens = response.json()
                logger.info(f"Fetched {len(tokens)} tokens from Jupiter")
                return tokens
                
        except Exception as e:
            logger.error(f"Error fetching Jupiter token list: {e}")
            return None
    
    async def create_limit_order(
        self,
        maker: str,
        input_mint: str,
        output_mint: str,
        making_amount: int,
        taking_amount: int,
        expiry: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Create a limit order (Jupiter Limit Order v2)
        
        Args:
            maker: Maker wallet public key
            input_mint: Input token mint
            output_mint: Output token mint
            making_amount: Amount of input token
            taking_amount: Minimum amount of output token
            expiry: Optional expiry timestamp
        
        Returns:
            Limit order transaction data
        """
        try:
            url = f"{self.limit_order_url}/createOrder"
            
            payload = {
                "maker": maker,
                "inputMint": input_mint,
                "outputMint": output_mint,
                "makingAmount": str(making_amount),
                "takingAmount": str(taking_amount)
            }
            
            if expiry:
                payload["expiredAt"] = expiry
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                order_data = response.json()
                logger.info(f"Created limit order for {maker[:8]}...")
                return order_data
                
        except Exception as e:
            logger.error(f"Error creating limit order: {e}")
            return None
    
    async def get_open_orders(self, wallet: str) -> Optional[List[Dict]]:
        """Get open limit orders for a wallet"""
        try:
            url = f"{self.limit_order_url}/orders"
            params = {"wallet": wallet, "status": "open"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                orders = response.json()
                return orders
                
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return None
