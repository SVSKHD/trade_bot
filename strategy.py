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

def is_bullish_trend(candles):
    return all(candles[i]['close'] > candles[i]['open'] for i in range(3))

def is_bearish_trend(candles):
    return all(candles[i]['close'] < candles[i]['open'] for i in range(3))

def strategy_decision(symbol, timeframe):
    candles = mt5.copy_rates_from_pos(symbol, timeframe, 0, 3)
    if candles is None or len(candles) < 3:
        print(f"Failed to get candle data for {symbol}, error code =", mt5.last_error())
        return 'hold'

    macd, signal = calculate_macd(symbol, timeframe)
    rsi = calculate_rsi(symbol, timeframe)

    if is_bullish_trend(candles) and macd > signal and rsi < 30:
        return 'buy'
    elif is_bearish_trend(candles) and macd < signal and rsi > 70:
        return 'sell'
    else:
        return 'hold'
