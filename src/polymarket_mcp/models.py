from pydantic import BaseModel
from typing import List, Optional, Any

class Market(BaseModel):
    id: str
    condition_id: str
    question: str
    tokens: List[Any]
    rewards: Optional[Any] = None
    active: bool
    closed: bool
    
class OrderBook(BaseModel):
    hash: str
    bids: List[Any]
    asks: List[Any]
    market: str
    timestamp: str


