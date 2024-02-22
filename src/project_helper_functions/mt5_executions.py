import MetaTrader5 as mt5


def buy_order(symbol: str, lot: float, price: float, deviation: list, stop_loss: float):
    res = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": price - stop_loss,
            "deviation": min(deviation),
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
    )
    if res != None:
        return f'BUY ORDER RESULT {symbol} - Ticket={res.order} - comment={res.comment}'
    else:
        return f'None Response From MT5'



def sell_order(symbol: str, lot: float, price: float, deviation: list, stop_loss: float):
    res = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": price + stop_loss,
            "deviation": min(deviation),
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
    )
    if res != None:
        return f'SELL ORDER RESULT {symbol} - Ticket={res.order} - comment={res.comment} - volume={res.volume}'
    else:
        return f'None Response From MT5'

def close_buy_order(price: float, deviation: list, position):
    res = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "position": position.ticket,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "deviation": min(deviation),
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
    )
    if res != None:
        return f'CLOSE BUY ORDER RESULT {position.symbol} - Ticket={position.ticket}' \
               f' - Comment={res.comment} - Volume={position.volume}'
    else:
        return f'None Response From MT5'


def close_sell_order(price: float, deviation: list, position):
    res = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "position": position.ticket,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "deviation": min(deviation),
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
    )
    if res != None:
        return f'CLOSE SELL ORDER RESULT {position.symbol} - Ticket={position.ticket}' \
               f' - Comment={res.comment} - Volume={position.volume}'
    else:
        return f'None Response From MT5'
