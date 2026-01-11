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

    def list_markets(self, limit: int = 100, closed: bool = False, slug: str = None, search: str = None):
        """
        Fetch markets from Gamma API which has better active/closed filtering.
        
        Args:
            limit: Max number of markets to return
            closed: Include closed markets
            slug: Filter by event slug (e.g. 'us-strike-on-mexico-by')
            search: Search in event/market title text
        """
        markets = []
        
        # If searching by slug or text, use events API which has better search
        if slug or search:
            event_params = {
                "_limit": limit,
                "closed": str(closed).lower(),
                "active": "true"
            }
            if slug:
                event_params["slug"] = slug
            if search:
                event_params["title_contains"] = search
            
            resp = requests.get(f"{GAMMA_API}/events", params=event_params, timeout=30)
            resp.raise_for_status()
            events = resp.json()
            
            # Extract markets from events
            for event in events:
                event_title = event.get("title")
                for m in event.get("markets", []):
                    m["_event_title"] = event_title  # Inject event title
                    markets.append(m)
        else:
            # Default: use markets endpoint
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
            
            # Get title from parent event if available
            # Check _event_title (injected from events search) or events array
            event_title = m.get("_event_title")
            if not event_title:
                events = m.get("events", [])
                event_title = events[0].get("title") if events else None
            title = event_title or m.get("question")
            
            result.append({
                "title": title,
                "condition_id": m.get("conditionId"),
                "question": m.get("question"),
                "description": m.get("description"),
                "market_slug": m.get("slug"),
                "active": m.get("active"),
                "closed": m.get("closed"),
                "tokens": tokens
            })
        
        return result

    def get_market_by_slug(self, slug: str):
        """Get a market by its URL slug (e.g. 'us-strike-on-mexico-by')."""
        markets = self.list_markets(limit=1, slug=slug)
        return markets[0] if markets else None

    def get_market(self, condition_id: str):
        return self.client.get_market(condition_id)

    def get_price(self, token_id: str, side: str = "buy"):
        return self.client.get_price(token_id, side=side)
    
    def get_midpoint(self, token_id: str):
        return self.client.get_midpoint(token_id)
        
    def get_orderbook(self, token_id: str):
        return self.client.get_order_book(token_id)


