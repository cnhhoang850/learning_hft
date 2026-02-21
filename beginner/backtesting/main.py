from data_loader import load_candles, resample_candles
from calculation import (
    add_moving_average,
    generate_signals,
    pct_change,
    calculate_strategy_returns,
    calculate_cumulative_returns,
    calculate_sharpe_ratio,
    calculate_drawdown,
)

def main():
    df = load_candles("BTCUSDT")
    df = resample_candles(df, '1h')
    df = add_moving_average(df)
    df = generate_signals(df)
    df = pct_change(df)
    df = calculate_strategy_returns(df)
    df = calculate_cumulative_returns(df)
    df = calculate_drawdown(df)

    sharpe = calculate_sharpe_ratio(df)
    total_return = df['cumulative_strategy_return'].iloc[-1]
    max_drawdown = df['drawdown'].min()

    print(f"Total Return: {total_return:.2%}")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2%}")

if __name__ == "__main__":
    main()