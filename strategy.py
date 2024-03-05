from MetaTrader5 import mt5
import pandas as pd

def calculate_macd(symbol, timeframe, fast_ema_period=12, slow_ema_period=26, signal_period=9):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, slow_ema_period + 100)
    df = pd.DataFrame(rates)
    df['fast_ema'] = df['close'].ewm(span=fast_ema_period, adjust=False).mean()
    df['slow_ema'] = df['close'].ewm(span=slow_ema_period, adjust=False).mean()
    df['macd'] = df['fast_ema'] - df['slow_ema']
    df['signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
    return df.iloc[-1]['macd'], df.iloc[-1]['signal']

def calculate_rsi(symbol, timeframe, period=14):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, period + 100)
    df = pd.DataFrame(rates)
    delta = df['close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def fibonacci_levels(high, low):
    levels = {
        '23.6%': high - (high - low) * 0.236,
        '38.2%': high - (high - low) * 0.382,
        '61.8%': high - (high - low) * 0.618,
        '78.6%': high - (high - low) * 0.786,
    }
    return levels

def ichimoku_cloud(df):
    df['tenkan_sen'] = (df['high'].rolling(window=9).max() + df['low'].rolling(window=9).min()) / 2
    df['kijun_sen'] = (df['high'].rolling(window=26).max() + df['low'].rolling(window=26).min()) / 2
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    df['senkou_span_b'] = ((df['high'].rolling(window=52).max() + df['low'].rolling(window=52).min()) / 2).shift(26)
    df['chikou_span'] = df['close'].shift(-26)
    return df

def is_bullish_trend(candles):
    return all(candles[i]['close'] > candles[i]['open'] for i in range(3))

def is_bearish_trend(candles):
    return all(candles[i]['close'] < candles[i]['open'] for i in range(3))

def strategy_decision(symbol, timeframe, pip_threshold=15):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 52 + 100)
    df = pd.DataFrame(rates)

    macd, signal = calculate_macd(symbol, timeframe)
    rsi = calculate_rsi(symbol, timeframe)
    ichimoku_df = ichimoku_cloud(df)

    last_candle = df.iloc[-1]
    prev_candle = df.iloc[-2]
    pip_movement = abs(last_candle['close'] - prev_candle['close']) / 0.0001

    live_price = last_candle['close']

    high = df['high'].iloc[-10:].max()
    low = df['low'].iloc[-10:].min()
    fib_levels = fibonacci_levels(high, low)

    strategies_passed = []
    if is_bullish_trend(df.iloc[-3:].to_dict('records')):
        strategies_passed.append('Bullish Trend')
    if macd > signal:
        strategies_passed.append('MACD > Signal')
    if rsi < 30:
        strategies_passed.append('RSI < 30')
    if last_candle['close'] > fib_levels['61.8%']:
        strategies_passed.append('Above 61.8% Fibonacci')
    if ichimoku_df.iloc[-1]['tenkan_sen'] > ichimoku_df.iloc[-1]['kijun_sen']:
        strategies_passed.append('Tenkan-sen > Kijun-sen')

    decision = 'hold'
    if strategies_passed and pip_movement >= pip_threshold:
        decision = 'buy' if 'Bullish Trend' in strategies_passed else 'sell'

    print(f"Symbol: {symbol}, Live Price: {live_price}, Strategies Passed: {', '.join(strategies_passed) if strategies_passed else 'None'}, Pip Difference: {pip_movement:.2f}, Trade Decision: {decision.upper()}")

    return decision
