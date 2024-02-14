import MetaTrader5 as mt5


def buy_order(symbol: str, lot: float, price: float, deviation: list):
    res = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            # "sl": price - 100 * point,
            # "tp": price + 100 * point,
            "deviation": min(deviation),
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
    )
    print(f'buy {symbol}', res, mt5.last_error())

    if res == None or res.order == 0:
        print('DIDNT GET FIRST PRICE')
        res = mt5.order_send(
            {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_BUY,
                "price": price,
                # "sl": price - 100 * point,
                # "tp": price + 100 * point,
                "deviation": max(deviation),
                "magic": 234000,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
        )
        print(f'buy {symbol}', res, mt5.last_error())
    if res == None or res.retcode != 10009:
        return None
    elif res.retcode == 10009:
        return res

def sell_order(symbol: str, lot: float, price: float, deviation: list):
    res = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "deviation": min(deviation),
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
    )
    print(f'sell {symbol}', res, mt5.last_error())
    if res == None or res.order == 0:
        res = mt5.order_send(
            {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_SELL,
                "price": price,
                "deviation": max(deviation),
                "magic": 234000,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
        )
        print(f'sell {symbol}', res, mt5.last_error())
    if res != None and res.retcode == 10009:
        return res
    else:
        return None

def close_buy_order(symbol: str, lot: float, price: float, deviation: list, position):
    res = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "position": position.order,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "deviation": min(deviation),
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
    )
    print('close buy', symbol, res)
    if res.retcode == 10009:
        return None
    else:
        return position

def close_sell_order(symbol: str, lot: float, price: float, deviation: list, position):
    res = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "position": position.order,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "deviation": min(deviation),
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
    )
    print('close sell', symbol, res)
    if res == None or res.order == 0 or res.retcode != 10009:
        res = mt5.order_send(
            {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "position": position.order,
                "type": mt5.ORDER_TYPE_BUY,
                "price": price,
                "deviation": max(deviation),
                "magic": 234000,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
        )
        print('close sell', symbol, res)
    if res.retcode == 10009:
        return None
    else:
        return position