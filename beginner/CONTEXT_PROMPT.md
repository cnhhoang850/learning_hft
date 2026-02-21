Act as a senior developer mentoring me through building scalable backend systems projects. Guide me but don't code for me unless I explicitly ask. Let me write the code and review it when I show you.

## Direction change
Pivoted from HFT-specific projects to backend/scalable systems — more broadly employable, less niche. The first 3 HFT projects are still valuable foundations (real-time streaming, ETL pipelines, data processing, Postgres, Docker).

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

### Project 3: Simple Vectorized Backtester — COMPLETE (beginner/backtesting/)
Built a vectorized backtester for a moving average crossover strategy using Pandas. Loads data from TimescaleDB, runs the strategy, and reports performance metrics.

#### What I built:
- **data_loader.py** — Data loading layer:
  - `load_candles()` — loads candles from TimescaleDB into a Pandas DataFrame using `pd.read_sql()` with parameterized queries
  - `resample_candles()` — aggregates 1-min candles to higher timeframes using `.resample().agg()` with OHLCV rules (open=first, high=max, low=min, close=last, volume=sum)
- **calculation.py** — Strategy and metrics:
  - `add_moving_average()` — computes short (20) and long (50) period rolling means on close price
  - `generate_signals()` — generates buy (+1) / sell (-1) signals based on MA crossover, with `.shift(1)` to create position column preventing look-ahead bias
  - `pct_change()` — computes bar-by-bar market returns via `.pct_change()`
  - `calculate_strategy_returns()` — multiplies position by market return (vectorized, no loops)
  - `calculate_cumulative_returns()` — compounds returns via `(1 + ret).cumprod() - 1` for both strategy and market
  - `calculate_sharpe_ratio()` — `mean / std * sqrt(8760)` annualized for hourly crypto bars
  - `calculate_drawdown()` — equity curve via `.cumprod()`, peak via `.cummax()`, drawdown = `(equity - peak) / peak`
- **main.py** — Pipeline: load → resample → MAs → signals → returns → cumulative → drawdown → print metrics

#### Results (BTCUSDT, ~25k 1-min candles → ~1000 hourly bars):
- Total Return: -19.82%
- Sharpe Ratio: 0.08
- Max Drawdown: -69.54%
- Conclusion: simple MA crossover is not profitable on this data — expected result, validates the backtester works correctly

#### Concepts I now understand:
- Vectorized computation — all operations on entire columns at once, no Python loops
- Look-ahead bias — the #1 backtesting trap. `.shift(1)` enforces "decide now, act next bar"
- Simple returns via `.pct_change()` — `(current - previous) / previous`
- Compound returns via `.cumprod()` — more accurate than `.cumsum()` because returns compound
- Sharpe ratio — `mean / std * sqrt(N)` measures risk-adjusted return. Mean scales linearly, std scales with sqrt(time), so annualization factor is sqrt(bars_per_year)
- Max drawdown — worst peak-to-trough decline, measures the worst pain during the strategy
- NaN propagation — rolling windows and shift create NaN rows that must be handled with `.fillna(0)` before `.cumprod()`
- Boolean indexing in Pandas — `df.loc[boolean_array, column]` selects rows where True
- OHLCV resampling rules — open=first, high=max, low=min, close=last, volume=sum
- Why small datasets are misleading — 83 bars showed Sharpe 3.24, full dataset showed 0.08
- Fully invested backtesting — always 100% in, either long or short, no position sizing
- Shorting — sell/borrow first, buy back later, profit if price goes down

#### Known gaps/shortcuts taken:
- No transaction costs or slippage
- No position sizing — always fully invested (100% capital at risk)
- Connection string hardcoded
- Single strategy (MA crossover), single symbol (BTCUSDT)
- No visualization (equity curve chart)
- Assumes ability to short (valid for futures, not all spot markets)
- `risk_free_rate` in Sharpe defaults to 0 (fine for crypto, not for comparing with traditional assets)
- `ORDER BY open_time DESC` in SQL — loads newest first, Pandas resample still works but sorting ASC would be more conventional

#### Key design decisions made:
- Vectorized over event-driven backtester (simpler, faster for this use case)
- Separate files for data loading vs calculation logic
- Functions return df for chaining (pipeline pattern)
- Annualization factor 8760 for crypto (24 * 365, not 252 stock trading days)
- `fillna(0)` only on return columns, not entire DataFrame (preserves MA NaN values)
- Compound returns (`cumprod`) over additive (`cumsum`) for accuracy

## Tech stack
- **Projects 1-3 (completed):** Python 3.14, uv, websocket-client, sortedcontainers, rich, requests, psycopg, pandas, numpy
- **Projects 4+ (current):** Go — learning Go through backend projects. New to Go, coming from Python.
- Database: TimescaleDB (Postgres extension) running in Docker on port 6543
- Working directory: learning_hft/

## Transferable skills from HFT projects
| HFT project | Backend skill |
|---|---|
| Project 1 (WebSocket feed) | Real-time streaming, pub/sub, data structures |
| Project 2 (ETL pipeline) | Data pipelines, Postgres, Docker, idempotency |
| Project 3 (Backtester) | SQL queries, data processing, pipeline pattern |

### Project 4: REST API Service — IN PROGRESS (beginner/rest-api/)
Building a REST API in Go serving candle data from TimescaleDB. First Go project.

#### What I've built so far:
- **main.go** — single-file API with:
  - `GET /health` — health check returning `{"status": "ok"}`
  - `GET /candles?symbol=BTCUSDT&limit=100&offset=0` — paginated candle query with input validation
  - `Candle` struct with JSON tags matching DB columns
  - `CandleResponse` wrapper struct with `data`, `limit`, `offset`, `count` for pagination metadata
  - `isNumber()` validation for query params
  - `connectToDatabase()` returning `(*pgx.Conn, error)` — caller owns and closes the connection
- **Database:** pgx driver connecting to existing TimescaleDB on port 6543
- **Dev tooling:** `air` for hot-reloading (`go install github.com/air-verse/air@latest`)

#### Go concepts I now understand:
- `package main` + `func main()` as entry point
- Imports with full paths (`"net/http"`, `"encoding/json"`)
- `:=` (declare+assign) vs `=` (reassign existing variable)
- Structs = Python dataclasses. JSON tags control serialization (`json:"field_name"`)
- Uppercase = exported (public), lowercase = unexported (private) — enforced by compiler
- `if err != nil` pattern everywhere — Go has no exceptions
- `defer` — schedules cleanup to run when the enclosing function returns, not when things hang
- `context.Background()` — root context with no timeout/cancellation
- `r.Context()` — request context, auto-cancels if client disconnects
- `&` (address-of) for `rows.Scan()` — Scan needs to write into your variables
- `_` to discard unused variables (e.g. `for _, ch := range s`)
- Go refuses to compile with unused imports or variables
- `http.HandleFunc` registers routes, handler signature is always `(http.ResponseWriter, *http.Request)`
- `http.Error(w, msg, code)` + `return` for error responses
- `json.NewEncoder(w).Encode(thing)` writes JSON directly to response
- Closures capture outer variables (used for passing `conn` to handlers)
- `nil` = Go's null. Zero values: `""` for string, `0` for int, `false` for bool
- Slices (`[]Candle{}`) = Go's dynamic arrays, `append()` to add elements
- Maps (`map[string]string{}`) = Go's dicts

#### Database access patterns in Go (from alexedwards.net/blog/organising-database-access):
1. **Global variable** — simplest, what we're using now. `var db *pgx.Conn` at package level. Fine for small apps, bad for testing.
2. **Dependency injection via struct** — `type Server struct { db *pgx.Conn }`, handlers are methods on Server. Clear dependencies, testable. Best for most apps.
3. **Dependency injection via closure** — handler functions return `http.HandlerFunc` that close over dependencies. Good for multi-package apps.
4. **Wrapping the connection pool** — custom types like `BookModel` wrapping `sql.DB`. Most abstracted, best for complex apps with interfaces/mocking.
5. **Request context** — `context.WithValue()`. Not recommended — loses type safety, hides dependencies.

#### REST API design principles learned:
- URL = noun (resource), HTTP method = verb (action)
- Plural nouns (`/candles` not `/candle`), lowercase, hyphens
- Query params for filtering (`?symbol=X`), pagination (`?limit=N&offset=M`)
- Validate at the boundary — convert/reject bad input before it reaches the DB
- Proper HTTP status codes: 200 OK, 400 Bad Request, 401 Unauthorized, 500 Internal
- Always `return` after `http.Error()` — otherwise handler keeps executing
- Wrap responses with metadata (`data`, `count`, `limit`, `offset`) for pagination
- Always quote URLs with `&` in shell commands

#### Known gaps/shortcuts:
- Using global variable for DB access (should be struct-based for production)
- Using `pgx.Conn` (single connection) instead of `pgxpool.Pool` (connection pool)
- Connection string hardcoded
- No authentication (JWT next)
- No rate limiting
- No tests

#### Key design decisions:
- Go over Python/FastAPI for backend projects (more employable for scalable systems)
- `net/http` standard library for now (no router framework yet)
- Single `main.go` file for simplicity while learning
- Global `var db` pattern (simplest — will refactor to struct pattern when adding more dependencies)

## Upcoming projects (scalable backend systems — in Go)

### Project 4: REST API Service
Build a proper API in Go with `net/http` / chi router, auth (JWT), pagination, filtering, rate limiting. Serve candle data from TimescaleDB over HTTP. Also serves as the "learn Go" project.

### Project 5: Job Queue / Background Workers
Producer/consumer pattern with Redis or RabbitMQ. Queue jobs, retry on failure, track status. Classic backend pattern.

### Project 6: Real-time Notification Service
Build a WebSocket *server* that fans out events to subscribers. Add pub/sub with Redis. Powers chat, dashboards, live feeds.

### Project 7: Event-driven Pipeline with Kafka
Distributed ETL. Multiple producers/consumers, guaranteed delivery, dead letter queues. What every data-heavy company runs.

### Project 8: URL Shortener at Scale
Classic system design interview question, actually built. Covers hashing, caching (Redis), analytics, rate limiting, horizontal scaling.
