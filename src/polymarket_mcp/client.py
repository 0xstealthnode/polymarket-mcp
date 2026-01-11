import os
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

HOST = "https://clob.polymarket.com"

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

    def list_markets(self):
        # py-clob-client doesn't have a direct 'get_all_markets' that is efficient without pagination or iteration
        # simplified_markets might be what we want, or sampling events
        # For now using get_simplified_markets/get_markets logic if available or falling back to events
        pass 
        # Actually py-clob-client methods vary. Let's use get_sampling_markets or similar if available, 
        # or just get_markets() with a limit.
        # Based on research, `get_simplified_markets` exists.
        return self.client.get_simplified_markets()

    def get_market(self, condition_id: str):
        return self.client.get_market(condition_id)

    def get_price(self, token_id: str, side: str = "buy"):
        return self.client.get_price(token_id, side=side)
    
    def get_midpoint(self, token_id: str):
        return self.client.get_midpoint(token_id)
        
    def get_orderbook(self, token_id: str):
        return self.client.get_order_book(token_id)


