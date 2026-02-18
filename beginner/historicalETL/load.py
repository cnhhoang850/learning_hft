# Connect to db 
# create table 
# insert idempotently? 
# primary key, unique
import psycopg
from dataclasses import astuple

def create_candles_table():
    print("Connecting to database")
    with psycopg.connect("dbname=postgres user=postgres password=password host=localhost port=6543") as conn:
        print("Connected to database")
        print("Creating table")
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS candles (
                symbol text NOT NULL,
                open_time bigint NOT NULL,
                open_price float NOT NULL,
                high_price float NOT NULL,
                low_price float NOT NULL,
                close_price float NOT NULL,
                close_time bigint NOT NULL,
                volume float NOT NULL,
                number_of_trades int NOT NULL,
                PRIMARY KEY (symbol, open_time)
                )
            """)
            print("Created candles table")

        conn.commit()

    return True


def insert_candles(candles):
    print("Connecting to database")

    with psycopg.connect("dbname=postgres user=postgres password=password host=localhost port=6543") as conn:

        print("Connected to database")

        with conn.cursor() as cur:
            for candle in candles:
                cur.execute("""
                    INSERT INTO candles (symbol, open_time, open_price, high_price, low_price, close_price, volume, close_time, number_of_trades)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, open_time) DO NOTHING
                """, astuple(candle))
                if cur.rowcount == 1:
                    print(f"Inserted candle: {candle.symbol} {candle.open_time}")
                else:
                    print(f"Skipped duplicate: {candle.symbol} {candle.open_time}")

        conn.commit()
