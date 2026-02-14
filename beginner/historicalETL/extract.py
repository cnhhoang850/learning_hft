import requests
from models import Candle
from datetime import datetime, timezone

def fetch_historical_data(api_url, params):
    response = requests.get(api_url, params=params)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()

def process_candle_binance(raw_data_entry, symbol):
    candle = Candle(
        symbol=symbol,
        open_time=raw_data_entry[0],
        open_price=float(raw_data_entry[1]),
        high_price=float(raw_data_entry[2]),
        low_price=float(raw_data_entry[3]),
        close_price=float(raw_data_entry[4]),
        volume=float(raw_data_entry[5]),
        close_time=raw_data_entry[6],
        number_of_trades=int(raw_data_entry[8])
    )
    return candle

def get_start_end_of_month_timestamps(year, month):
    """Returns the start and end timestamps (in milliseconds) for the given month and year in current run context timezone."""
    if year is None or month is None:
        now = datetime.now(timezone.utc)
        year = now.year
        month = now.month
    start_of_month = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end_of_month = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end_of_month = datetime(year, month + 1, 1, tzinfo=timezone.utc)
    return int(start_of_month.timestamp() * 1000), int(end_of_month.timestamp() * 1000)

def fetch_binance_candles_monthly(symbol, month=None, year=None):
    monthly_candles = []
    api_url = "https://api.binance.com/api/v3/klines" 
    start_ts, end_ts = get_start_end_of_month_timestamps(year, month)
    print(f"Fetching data for {symbol} from {datetime.fromtimestamp(start_ts/1000)} {timezone.utc} to {datetime.fromtimestamp(end_ts/1000)} {timezone.utc}")
    query_timestamp = start_ts

    while query_timestamp < end_ts:
        params = {
            "symbol": symbol,
            "interval": "1m",
            "startTime": query_timestamp,
            "endTime": end_ts,
            "limit": 1000
        }
        raw_data = fetch_historical_data(api_url, params)
        print(f"Fetched {len(raw_data)} entries starting from {datetime.fromtimestamp(query_timestamp/1000)} {timezone.utc}")
        if not raw_data:
            break
        for entry in raw_data:
            candle = process_candle_binance(entry, symbol)
            monthly_candles.append(candle)
        query_timestamp = raw_data[-1][0] + 1  # Move to the next timestamp after the last fetched candle
    
    if not monthly_candles:
        print("No data fetched for the specified month.")
    

    return monthly_candles