# Market Data Feed Parser - Key Learnings

## WebSocket Connections
- Binance streams real-time market data over WebSocket at `wss://stream.binance.com:9443/ws`
- You subscribe to specific streams by sending a JSON message with `method: "SUBSCRIBE"` and a `params` list
- Must handle ping/pong to keep the connection alive

## Depth Stream & Deltas
- The depth stream (`btcusdt@depth@100ms`) sends **deltas**, not full snapshots
- Each message only contains price levels that **changed** since the last update
- A quantity of `0` means that price level was removed — must delete it, not store it
- Binance batches changes on their side every 100ms and sends one message — apply all updates immediately

## Order Book
- Two sides: **bids** (buyers, sorted descending) and **asks** (sellers, sorted ascending)
- Best bid = highest buy price, best ask = lowest sell price
- **Spread** = best ask - best bid (should always be positive; negative means a bug)
- **Mid price** = (best bid + best ask) / 2
- Used `SortedDict` from `sortedcontainers` for O(log n) insert/delete with always-sorted keys
- Best bid via `peekitem(-1)`, best ask via `peekitem(0)`

## Data Normalization
- Raw exchange data should be parsed into a **normalized format** (the `Tick` dataclass)
- Normalization makes data exchange-agnostic — same `Tick` format can work for Binance, Alpaca, etc.
- Used Python `@dataclass` for clean, structured data representation
- Fields: symbol, bid, ask, bid_qty, ask_qty, spread, mid_price, event_time

## Market Microstructure Concepts
- **Spread widening** = volatility/momentum, but doesn't indicate direction on its own
- To determine direction: track which side moved (best bid dropped vs best ask jumped)
- **Order book imbalance** (more volume on bids vs asks) can signal price direction
- Thin levels (low quantity at best price) mean price can move easily with small orders

## Python Patterns Used
- `websocket-client` library with `WebSocketApp` for callback-based WebSocket handling
- `dataclass` for structured, typed data models
- `SortedDict` for maintaining sorted key-value state
- `rich` library with `Live` display for real-time terminal UI
- Separating concerns: `main.py` (connection), `order_book.py` (state), `models.py` (data), `display.py` (visualization)
