# Contents of execution.py

from MetaTrader5 import mt5
import threading
from trade_management import initialize_mt5, place_trade, close_trade, shutdown_mt5
from strategy import strategy_decision

def monitor_symbol(symbol, timeframe):
    decision = strategy_decision(symbol, timeframe)

    if decision == 'buy':
        print(f"Strategy decision for {symbol}: BUY")
        # Example: place_trade(symbol, 0.01, mt5.ORDER_TYPE_BUY, 100, 300, "Strategy buy order")
    elif decision == 'sell':
        print(f"Strategy decision for {symbol}: SELL")
        # Example: place_trade(symbol, 0.01, mt5.ORDER_TYPE_SELL, 100, 300, "Strategy sell order")
    else:
        print(f"Strategy decision for {symbol}: HOLD")

def main():
    if not initialize_mt5():
        print("Failed to initialize MT5, exiting.")
        return

    symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "XAGUSD"]
    timeframe = mt5.TIMEFRAME_M15
    threads = []

    for symbol in symbols:
        t = threading.Thread(target=monitor_symbol, args=(symbol, timeframe))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    shutdown_mt5()

if __name__ == "__main__":
    main()
