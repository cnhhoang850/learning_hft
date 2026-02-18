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

### Project 2: Historical Data Pipeline — COMPLETE (beginner/historicalETL/)
Built an ETL pipeline that ingests, cleans, and stores OHLCV candle data into TimescaleDB.

#### What I built:
- **models.py** — `Candle` dataclass (symbol, open_time, open_price, high_price, low_price, close_price, volume, close_time, number_of_trades)
- **extract.py** — Complete extraction layer:
  - `fetch_historical_data()` — raw REST call to Binance `/api/v3/klines`
  - `process_candle_binance()` — maps Binance array response to `Candle` dataclass (index-based mapping)
  - `get_start_end_of_month_timestamps()` — generates start/end ms timestamps for a given month/year, defaults to current month
  - `fetch_binance_candles_monthly()` — paginated fetch (loops in batches of 1000, advances `startTime` by last candle's `open_time + 1`)
- **transform.py** — Data quality validation:
  - `check_candle_data_quality()` — validates OHLC consistency (high >= open/low/close, low <= open/high/close), negative volume, null fields (null check runs first to avoid TypeError)
  - `check_missing_minutes()` — gap detection between consecutive candles (expects 60,000ms intervals)
  - `check_duplicate_minutes()` — duplicate detection using set length comparison on `open_time`
- **load.py** — Database loading layer:
  - `create_candles_table()` — creates table with `IF NOT EXISTS`, composite primary key `(symbol, open_time)`
  - `insert_candles()` — idempotent inserts using `INSERT ... ON CONFLICT DO NOTHING`, uses `dataclasses.astuple()` for value mapping
- **main.py** — Orchestrator: extract → validate → load
- **Database** — TimescaleDB (Postgres extension) running in Docker on port 6543, ~24,858 candles loaded

#### Concepts I now understand:
- OHLCV candle structure and what each field represents
- ETL pattern — Extract/Transform/Load with separation of concerns
- Pagination for REST APIs (Binance 1000 candle limit per request)
- Data normalization — one parser per exchange, all output same `Candle` dataclass
- Why time-series databases exist (chunk-based storage, compression, time-range query optimization)
- Hypertables — automatic time-based partitioning for chunk exclusion, compression, and efficient inserts
- Data quality matters: garbage in = garbage out for backtesting
- Clean before load, not after (cheaper in memory, enforces schema, limits blast radius of bad data)
- Composite primary keys — `(symbol, open_time)` because multiple symbols share the same timestamps
- Idempotent inserts — `ON CONFLICT DO NOTHING` so re-running the pipeline doesn't create duplicates
- Duplicate detection — set-based O(n) approach vs O(n log n) sort-based
- Database transactions — batch all inserts, commit once (not per row)
- Never use f-strings for SQL values (SQL injection) — use parameterized queries with `%s` placeholders
- Error handling philosophy in ETLs — let it crash on infra failures (DB down, bad SQL), only handle expected data issues

#### Known gaps/shortcuts taken:
- Bad candles are detected but still loaded (no filter step before insert)
- `datetime.fromtimestamp()` shows local time but labels say UTC in extract.py and transform.py
- Connection string hardcoded in three places (should be env var, defined once)
- Print statements instead of proper logging
- Row-by-row inserts (works but `execute_values` or `COPY` would be 10-50x faster at scale)
- Single symbol (BTCUSDT), single month only — no CLI args for symbol/date range
- `float` for prices (aware of precision issues, `Decimal` for production)
- Table not converted to hypertable yet
- No post-load verification (row count comparison)
- No retry logic on Binance API calls

#### Key design decisions made:
- TimescaleDB over QuestDB (Postgres ecosystem, transferable SQL skills)
- Composite primary key `(symbol, open_time)` over synthetic auto-increment ID (natural key enables idempotency, no meaningless columns)
- Timestamps stored as `int` (ms) in dataclass, `BIGINT` in Postgres
- One parser function per exchange for normalization
- Pagination uses `open_time + 1` offset to avoid duplicates
- Each function manages its own DB connection (simple, no connection passing)

## Tech stack
- Python 3.14, uv package manager
- Libraries: websocket-client, sortedcontainers, rich, requests, psycopg
- Database: TimescaleDB (Docker, port 6543)
- Working directory: learning_hft/
