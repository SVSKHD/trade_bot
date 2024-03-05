from MetaTrader5 import mt5
from trade_management import initialize_mt5, place_trade, close_trade, shutdown_mt5
from strategy import strategy_decision
import threading

def monitor_symbol(symbol, timeframe):
    decision = strategy_decision(symbol, timeframe)

    if decision == 'buy':
        print(f"Strategy decision for {symbol}: BUY")
        ticket = place_trade(symbol, 0.01, mt5.ORDER_TYPE_BUY, 100, 300, comment="Strategy buy order")
        # Additional logic to manage the trade
    elif decision == 'sell':
        print(f"Strategy decision for {symbol}: SELL")
        ticket = place_trade(symbol, 0.01, mt5.ORDER_TYPE_SELL, 100, 300, comment="Strategy sell order")
        # Additional logic to manage the trade
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
