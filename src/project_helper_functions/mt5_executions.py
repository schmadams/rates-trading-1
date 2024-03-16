import MetaTrader5 as mt5


def buy_order(symbol: str, lot: float, ask_price: float, bid_price: float, deviation: list, stop_loss: float, take_profit: float):
    res = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": ask_price,
            "sl": bid_price - 1.5*stop_loss,
            "tp": ask_price + take_profit,
            "deviation": min(deviation),
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
    )
    if res != None:
        return f'BUY ORDER RESULT {symbol} - Ticket={res.order} - comment={res.comment} - volume={res.volume} - price={res.price}'
    else:
        return f'None Response From MT5 {mt5.last_error()}'



def sell_order(symbol: str, lot: float, ask_price: float, bid_price: float, deviation: list, stop_loss: float, take_profit: float):
    res = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": bid_price,
            "tp": bid_price - take_profit,
            "sl": ask_price + stop_loss,
            "deviation": min(deviation),
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
    )
    if res != None:
        return f'SELL ORDER RESULT {symbol} - Ticket={res.order} - comment={res.comment} - volume={res.volume} - price={res.price}'
    else:
        return f'None Response From MT5 {mt5.last_error()}'

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
               f' - Comment={res.comment} - Volume={position.volume} price={res.price}'
    else:
        return f'None Response From MT5 {mt5.last_error()}'


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
               f' - Comment={res.comment} - Volume={position.volume} - price={res.price}'
    else:
        return f'None Response From MT5 {mt5.last_error()}'
