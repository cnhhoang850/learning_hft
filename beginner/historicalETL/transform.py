from datetime import datetime

def check_candle_data_quality(candle):
    for field in candle.__dataclass_fields__:
        if field == "high_price": 
            diffs = [candle.high_price - candle.open_price, 
                     candle.high_price - candle.low_price, 
                     candle.high_price - candle.close_price]
            if any(diff < 0 for diff in diffs):
                print(f"Data quality issue: high_price {candle.high_price} is less than one of open_price, low_price, or close_price in candle {candle}")
                return False
        
        if field == "volume" and candle.volume < 0:
            print(f"Data quality issue: volume {candle.volume} is negative in candle {candle}")
            return False

        value = getattr(candle, field)
        if value is None:
            print(f"Data quality issue: {field} is None in candle {candle}")
            return False
    return True
        
def check_mising_minutes(candles): 
    if not candles:
        print("No candles to check for missing minutes.")
        return
    
    candles.sort(key=lambda c: c.open_time)  # Ensure candles are sorted by open_time
    expected_interval = 60 * 1000  # 1 minute in milliseconds

    for i in range(1, len(candles)):
        time_diff = candles[i].open_time - candles[i-1].open_time
        if time_diff > expected_interval:
            print(f"Missing minutes detected between {datetime.fromtimestamp(candles[i-1].open_time/1000)} and {datetime.fromtimestamp(candles[i].open_time/1000)}. Time difference: {time_diff} ms")

    return True
    