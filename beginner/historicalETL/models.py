
from dataclasses import dataclass 

@dataclass
class Candle:
    """Represents a candle data point."""
    symbol: str
    open_time: int
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    close_time: int
    number_of_trades: int

