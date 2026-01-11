import os
import requests
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

HOST = "https://clob.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"

class PolymarketClient:
    def __init__(self):
        self.key = os.getenv("POLYMARKET_PRIVATE_KEY")
        self.proxy_address = os.getenv("POLYMARKET_PROXY_ADDRESS")
        self.chain_id = int(os.getenv("POLYMARKET_CHAIN_ID", 137))
        self.client = self._init_client()

    def _init_client(self) -> ClobClient:
        if not self.key:
            # Read-only mode
            return ClobClient(HOST)
        
        if self.proxy_address:
            # Proxy/Email wallet
            client = ClobClient(
                HOST,
                key=self.key,
                chain_id=self.chain_id,
                signature_type=1, # Default to Email/Magic
                funder=self.proxy_address
            )
        else:
            # EOA Direct
            client = ClobClient(
                HOST,
                key=self.key,
                chain_id=self.chain_id
            )
            
        try:
            client.set_api_creds(client.create_or_derive_api_creds())
        except Exception as e:
            print(f"Warning: Failed to derive API creds for trading: {e}")
            
        return client

    def list_markets(self, limit: int = 50, closed: bool = False):
        """
        Fetch markets from Gamma API which has better active/closed filtering.
        The CLOB API's get_simplified_markets returns old markets first.
        """
        params = {
            "limit": limit,
            "closed": str(closed).lower(),
            "active": "true"
        }
        resp = requests.get(f"{GAMMA_API}/markets", params=params, timeout=30)
        resp.raise_for_status()
        markets = resp.json()
        
        # Parse token IDs from JSON strings and format response
        result = []
        for m in markets:
            try:
                clob_token_ids = eval(m.get("clobTokenIds", "[]")) if m.get("clobTokenIds") else []
                outcomes = eval(m.get("outcomes", "[]")) if m.get("outcomes") else []
                outcome_prices = eval(m.get("outcomePrices", "[]")) if m.get("outcomePrices") else []
            except:
                clob_token_ids, outcomes, outcome_prices = [], [], []
            
            tokens = []
            for i, token_id in enumerate(clob_token_ids):
                tokens.append({
                    "token_id": token_id,
                    "outcome": outcomes[i] if i < len(outcomes) else "Unknown",
                    "price": float(outcome_prices[i]) if i < len(outcome_prices) else None
                })
            
            result.append({
                "condition_id": m.get("conditionId"),
                "question": m.get("question"),
                "description": m.get("description"),
                "market_slug": m.get("slug"),
                "active": m.get("active"),
                "closed": m.get("closed"),
                "tokens": tokens
            })
        
        return result

    def get_market(self, condition_id: str):
        return self.client.get_market(condition_id)

    def get_price(self, token_id: str, side: str = "buy"):
        return self.client.get_price(token_id, side=side)
    
    def get_midpoint(self, token_id: str):
        return self.client.get_midpoint(token_id)
        
    def get_orderbook(self, token_id: str):
        return self.client.get_order_book(token_id)


