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

### Project 2: Historical Data Pipeline — IN PROGRESS (beginner/historicalETL/)
Building an ETL pipeline that ingests, cleans, and stores OHLCV data into a time-series DB.

#### What I've built so far:
- **models.py** — `Candle` dataclass (symbol, open_time, open_price, high_price, low_price, close_price, volume, close_time, number_of_trades)
- **extract.py** — Complete extraction layer:
  - `fetch_historical_data()` — raw REST call to Binance `/api/v3/klines`
  - `process_candle_binance()` — maps Binance array response to `Candle` dataclass (index-based mapping)
  - `get_start_end_of_month_timestamps()` — generates start/end ms timestamps for a given month/year, defaults to current month
  - `fetch_binance_candles_monthly()` — paginated fetch (loops in batches of 1000, advances `startTime` by last candle's `open_time + 1`)
- **transform.py** — Quality checks (partially complete):
  - `check_candle_data_quality()` — validates OHLC consistency (high >= open/low/close), negative volume, null fields
  - `check_mising_minutes()` — gap detection between consecutive candles (expects 60,000ms intervals)
- **main.py** — Thin orchestrator that calls extract then runs quality checks

#### Concepts I now understand:
- OHLCV candle structure and what each field represents
- ETL pattern — Extract/Transform/Load with separation of concerns
- Pagination for REST APIs (Binance 1000 candle limit per request)
- Data normalization — one parser per exchange, all output same `Candle` dataclass
- Why time-series databases exist (chunk-based storage, compression, time-range query optimization)
- Data quality matters: garbage in = garbage out for backtesting
- Clean before load, not after (cheaper in memory, enforces schema, limits blast radius of bad data)

#### Review feedback to address (next steps):
1. **Missing low_price check** — need to validate `low <= open, high, close` (only checking high currently)
2. **No duplicate detection** — need to check for candles with same `open_time`
3. **Refactor quality check loop** — the `for field in __dataclass_fields__` pattern is over-engineered; use explicit checks instead
4. **Typo** — `check_mising_minutes` → `check_missing_minutes`
5. **Decide bad candle strategy** — drop, flag, or fail pipeline? (need to think about: wrong data is worse than missing data for trading)
6. **Print timestamp bug** — `datetime.fromtimestamp()` shows local time but label says UTC; use `datetime.fromtimestamp(ts/1000, tz=timezone.utc)` instead

#### Still TODO:
- Fix quality checks per review feedback above
- Build `load.py` — choose TimescaleDB or QuestDB, set up Docker container, create table schema, implement idempotent inserts
- Build `quality.py` if separating quality checks from transform
- Wire up full pipeline in `main.py`: extract → transform/validate → load
- Add basic logging instead of print statements

#### Key design decisions made:
- Using `float` for prices (aware of precision issues, `Decimal` for production)
- Timestamps stored as `int` (ms) in dataclass, conversion to `datetime` happens in transform
- One parser function per exchange for normalization
- Pagination uses `open_time + 1` offset to avoid duplicates

## Tech stack
- Python 3.14, uv package manager
- Libraries: websocket-client, sortedcontainers, rich, requests
- Working directory: learning_hft/
