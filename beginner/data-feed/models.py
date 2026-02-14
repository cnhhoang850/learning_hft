from dataclasses import dataclass 

@dataclass
class Tick:
    """Represents a market ticker data point."""
    symbol: str
    last_price: float
    event_time: int
    bid: float
    ask: float
    volume: float
    spread: float
    mid_price: float
    bid_qty: float
    ask_qty: float
