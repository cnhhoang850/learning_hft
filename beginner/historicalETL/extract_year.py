import sys
from extract import fetch_binance_candles_monthly
from transform import check_candle_data_quality, check_missing_minutes, check_duplicate_minutes
from load import create_candles_table, insert_candles

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_year.py <symbol> <year>")
        print("Example: python extract_year.py BTCUSDT 2024")
        sys.exit(1)

    symbol = sys.argv[1]
    year = int(sys.argv[2])

    create_candles_table()

    all_candles = []
    for month in range(1, 13):
        print(f"\n--- Fetching {symbol} for {year}-{month:02d} ---")
        candles = fetch_binance_candles_monthly(symbol, month=month, year=year)

        for candle in candles:
            if not check_candle_data_quality(candle):
                print(f"Data quality issue found in candle: {candle}")

        check_missing_minutes(candles)
        check_duplicate_minutes(candles)

        print(f"Fetched {len(candles)} candles for {year}-{month:02d}")
        insert_candles(candles)
        all_candles.extend(candles)

    print(f"\nTotal candles fetched for {symbol} in {year}: {len(all_candles)}")
