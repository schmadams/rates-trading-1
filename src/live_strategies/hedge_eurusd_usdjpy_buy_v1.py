import MetaTrader5 as mt5
from src.project_helper_functions.mt5_engine import mt5_connect_and_auth

class EURUSDJPYHedgeBuy:

    def __init__(self, lot, max_trades, wait_time):
        self.lot = lot
        self.max_trades = max_trades
        self.wait_time = wait_time
        self.get_positions()
        a=1
        a=1

    def get_positions(self):
        eu_pos = [pos for pos in mt5.positions_get(symbol="EURUSD") if pos.comment == 'eujhb']
        us_pos = [pos for pos in mt5.positions_get(symbol="USDJPY") if pos.comment == 'eujhb']
        return eu_pos, us_pos

    def run__live_strategy(self):

        while True:
            eu_pos, us_pos = self.get_positions()

            if len(eu_pos) < self.max_trades and len(us_pos) < self.max_trades:



if __name__ == '__main__':
    mt5_connect_and_auth(strategy='demo_hedge_buy')
    EURUSDJPYHedgeBuy(lot=0.01, max_trades=5, wait_time=60)