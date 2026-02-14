from sortedcontainers import SortedDict
from models import Tick

class OrderBook:
    def __init__(self):
        self.symbol = ""
        self.bids = SortedDict()
        self.prev_bid = None
        self.asks = SortedDict()
        self.prev_ask = None
     
    def update(self, bid_updates, ask_updates):
        self.prev_bid = self.bids.peekitem(-1) if self.bids else None
        self.prev_ask = self.asks.peekitem(0) if self.asks else None
        for price, qty in bid_updates:
            if qty == 0:
                if price in self.bids:
                    del self.bids[price]
            else:
                self.bids[price] = qty
        for price, qty in ask_updates:
            if qty == 0:
                if price in self.asks:
                    del self.asks[price]
            else:
                self.asks[price] = qty

    def peek_item(self, side, index):
        if side == 'bid':
            return self.bids.peekitem(index)
        elif side == 'ask':
            return self.asks.peekitem(index)
        else:
            raise ValueError("Side must be either 'bid' or 'ask'")
    
    def get_spread(self): 
        return self.asks.peekitem(0)[0] - self.bids.peekitem(-1)[0]
    
    def to_tick(self):
        mid_price = (self.bids.peekitem(-1)[0] + self.asks.peekitem(0)[0]) / 2
        spread = self.get_spread()
        return Tick(
            symbol=self.symbol,
            last_price=mid_price,
            event_time=0,
            bid=self.bids.peekitem(-1)[0],
            ask=self.asks.peekitem(0)[0],
            volume=0.0,
            spread=spread,
            mid_price=mid_price,
            bid_qty=self.bids.peekitem(-1)[1],
            ask_qty=self.asks.peekitem(0)[1]
        )

