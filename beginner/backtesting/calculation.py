
def add_moving_average(df, short_window=20, long_window=50):
    df['ma_short'] = df['close_price'].rolling(window=short_window).mean()
    df['ma_long'] = df['close_price'].rolling(window=long_window).mean()
    return df

def generate_signals(df):
    df['signal'] = 0
    df.loc[df['ma_short'] > df['ma_long'], 'signal'] = 1
    df.loc[df['ma_short'] < df['ma_long'], 'signal'] = -1
    df['position'] = df['signal'].shift(1)  # Shift signals to avoid look-ahead bias
    return df

def pct_change(df):
    df['pct_change'] = df['close_price'].pct_change()
    return df

def calculate_strategy_returns(df):
    df['strategy_return'] = df['position'] * df['pct_change']
    return df

def calculate_cumulative_returns(df):
    df['strategy_return'] = df['strategy_return'].fillna(0)  # Fill NaN values with 0 for cumulative return calculation
    df['pct_change'] = df['pct_change'].fillna(0)  # Fill NaN values with 0 for cumulative return calculation
    df['cumulative_strategy_return'] = (1 + df['strategy_return']).cumprod() - 1
    df['cumulative_market_return'] = (1 + df['pct_change']).cumprod() - 1
    return df

def calculate_sharpe_ratio(df, risk_free_rate=0.0, annualization_factor=8760):
    excess_return = df['strategy_return'] - risk_free_rate
    sharpe_ratio = excess_return.mean() / excess_return.std() * (annualization_factor ** 0.5)  # Annualize the Sharpe ratio
    return sharpe_ratio

def calculate_drawdown(df):
    equity = (1 + df['strategy_return']).cumprod()
    peak_equity = equity.cummax()
    drawdown = (equity - peak_equity) / peak_equity
    df['drawdown'] = drawdown
    return df