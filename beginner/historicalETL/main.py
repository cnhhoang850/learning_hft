from extract import fetch_binance_candles_monthly
from transform import check_candle_data_quality, check_missing_minutes, check_duplicate_minutes
from load import create_candles_table, insert_candles

if __name__ == "__main__": 
    candles = fetch_binance_candles_monthly("BTCUSDT")
    for candle in candles:
        if not check_candle_data_quality(candle):
            print(f"Data quality issue found in candle: {candle}")
    check_missing_minutes(candles)
    check_duplicate_minutes(candles)
    print(f"Fetched {len(candles)} candles.")
    print(candles[:5])  # Print first 5 candles for verification
    create_candles_table()
    print("Inserting candles")
    insert_candles(candles)


