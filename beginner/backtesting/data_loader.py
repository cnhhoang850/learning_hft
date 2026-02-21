import pandas as pd 
import psycopg as psql

def load_candles(symbol):
    print("Connecting to db")
    with psql.connect("dbname=postgres user=postgres password=password host=localhost port=6543") as conn:
        with conn.cursor() as cur: 
            df = pd.read_sql("SELECT * FROM candles WHERE symbol = %s", conn, params=(symbol,))
        conn.commit()
    return df

def resample_candles(df, timeframe):
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df.set_index('open_time', inplace=True)
    resampled = df.resample(timeframe).agg({
        'open_price': 'first',
        'high_price': 'max',
        'low_price': 'min',
        'close_price': 'last',
        'volume': 'sum'
    }).dropna()
    return resampled

