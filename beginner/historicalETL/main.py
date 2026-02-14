from extract import fetch_binance_candles_monthly
from transform import check_candle_data_quality, check_mising_minutes

if __name__ == "__main__":
    candles = fetch_binance_candles_monthly("BTCUSDT")
    for candle in candles:
        if not check_candle_data_quality(candle):
            print(f"Data quality issue found in candle: {candle}")
    check_mising_minutes(candles)
    print(f"Fetched {len(candles)} candles.")
    print(candles[:5])  # Print first 5 candles for verification