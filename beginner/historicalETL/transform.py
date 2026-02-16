from datetime import datetime

def check_candle_data_quality(candle):
    high_price = candle.high_price
    close_price = candle.close_price
    open_price = candle.open_price
    low_price = candle.low_price
    volume = candle.volume

    if (high_price - open_price < 0
        or high_price - close_price < 0
        or high_price -  low_price < 0): 
        print(f"Data quality issue: high_price {candle.high_price} is less than one of open_price, low_price, or close_price in candle {candle}")
        return False

    if (open_price - low_price < 0
        or close_price - low_price < 0
        or high_price - low_price < 0):
        print(f"Data quality issue: open_price {candle.open_price}, close_price {candle.close_price}, high_price {candle.high_price} are all less than low_price {candle.low_price} in candle {candle}")
        return False

    if volume < 0:
        print(f"Data quality issue: volume {candle.volume} is negative in candle {candle}")
        return False

    if any (value is None for value in (high_price, close_price, open_price, low_price, volume)):
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

