Act as a senior developer mentoring me through building HFT (High Frequency Trading) projects in Python. Guide me but don't code for me unless I explicitly ask. Let me write the code and review it when I show you.

## What I've completed

### Project 1: Market Data Feed Parser (beginner/data-feed/)
- Built a real-time WebSocket connection to Binance (`wss://stream.binance.com:9443/ws`)
- Subscribed to `btcusdt@depth@100ms` depth stream
- Built an `OrderBook` class using `SortedDict` from `sortedcontainers` that:
  - Maintains sorted bids (ascending, best bid via `peekitem(0)`) and asks (ascending, best ask via `peekitem(0)`)
  - Applies deltas from the depth stream (insert/update when qty > 0, delete when qty == 0)
  - Tracks previous best bid/ask for detecting which side moved
  - Computes spread, mid price
  - Outputs a normalized `Tick` dataclass (symbol, bid, ask, bid_qty, ask_qty, spread, mid_price, event_time)
- Built a live terminal visualization using `rich` library showing top 10 levels of the order book
- Used `websocket-client` library with `WebSocketApp` callback pattern

### Key concepts I now understand:
- Order book structure (bids/asks, price levels, quantities)
- Deltas vs snapshots (depth stream sends changes, not full book)
- Spread (always positive, negative = bug/crossed book)
- Mid price = (best_bid + best_ask) / 2
- Spread widening = volatility but doesn't indicate direction alone
- Data normalization — exchange-agnostic format via dataclass
- SortedDict for O(log n) sorted key-value operations

### Known gaps/shortcuts I took:
- No initial REST snapshot — book starts empty and builds from deltas only
- `event_time` hardcoded to 0 (not reading `E` field from depth messages)
- `last_price` and `volume` set to placeholder values (would need @trade or @ticker stream)
- No error handling for empty book in `to_tick()` / `get_spread()`

## Tech stack
- Python 3.14, uv package manager
- Libraries: websocket-client, sortedcontainers, rich
- Working directory: learning_hft/

## What's next
I'm ready for the next beginner HFT project. Suggest what I should build next and guide me through it step by step.
