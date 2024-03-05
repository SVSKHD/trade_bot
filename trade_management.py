# Contents of trademanagement.py

import MetaTrader5 as mt5

def initialize_mt5():
    """Initialize MT5 connection."""
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        quit()

def place_trade(symbol, volume, order_type, sl_points, tp_points, deviation=20, magic=123456, comment=""):
    """Place a trade on MT5."""
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select {symbol}, error code =", mt5.last_error())
        return None

    price = mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
    point = mt5.symbol_info(symbol).point

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": price - sl_points * point if order_type == mt5.ORDER_TYPE_BUY else price + sl_points * point,
        "tp": price + tp_points * point if order_type == mt5.ORDER_TYPE_BUY else price - tp_points * point,
        "deviation": deviation,
        "magic": magic,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to send order, retcode =", result.retcode)
        return None

    print(f"Order placed successfully, ticket = {result.order}")
    return result.order

def close_trade(symbol, volume, order_type, position, deviation=20, magic=123456, comment=""):
    """Close a trade on MT5."""
    price = mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(symbol).bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL if order_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
        "position": position,
        "price": price,
        "deviation": deviation,
        "magic": magic,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to close order, retcode =", result.retcode)
        return False

    print(f"Trade closed successfully, ticket = {result.order}")
    return True

def shutdown_mt5():
    """Shut down MT5 connection."""
    mt5.shutdown()
