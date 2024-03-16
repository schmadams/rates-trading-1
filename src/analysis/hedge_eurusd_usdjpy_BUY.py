import MetaTrader5 as mt5
import pandas as pd

from src.project_helper_functions.mt5_engine import mt5_connect_and_auth
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
class HedgeEURUSDJPY_BUY:
    def __init__(self, run_start, run_end, timeframe, symbols):
        self.start = run_start
        self.timeframe = timeframe
        self.end = run_end
        self.symbols = symbols
        self.get_run_data()
        self.run_strategy()


    def run_strategy(self):
        sl, tp = 250, 750
        lot, max_trades = 0.01, 2000
        eu_pos, uj_pos = [], []
        eu_prof, uj_prof = 0, 0
        winners, losers = 0, 0
        win_count, lose_count = 0, 0
        results = []
        eu_pip, uj_pip = mt5.symbol_info('EURUSD').point, mt5.symbol_info('USDJPY').point
        for row in self.data.itertuples():
            # print(len(eu_pos), len(uj_pos))
            if len(eu_pos) < max_trades:
                open_trade = ('EURUSD', lot, row.EURUSD_close + row.EURUSD_spread*eu_pip/2, row.time,
                              row.EURUSD_spread, row.EURUSD_close - sl*row.EURUSD_spread*eu_pip,
                              row.EURUSD_close + tp*row.EURUSD_spread*eu_pip)

                eu_pos.append(open_trade)
            if len(uj_pos) < max_trades:
                open_trade = ('USDJPY', lot, row.USDJPY_close + row.USDJPY_spread*uj_pip/2, row.time,
                              row.USDJPY_spread, row.USDJPY_close - sl*row.USDJPY_spread*uj_pip,
                              row.USDJPY_close + tp*row.USDJPY_spread*uj_pip)
                uj_pos.append(open_trade)

            if len(eu_pos) > 0:
                for idx, pos in enumerate(eu_pos):
                    if row.EURUSD_close >= pos[6]:
                        take_profit = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[0], pos[1], pos[2], pos[6])
                        # print(f'take profit EURUSD = {take_profit}')
                        eu_prof += take_profit
                        winners += take_profit
                        win_count += 1
                        del eu_pos[idx]
                    elif row.EURUSD_close <= pos[5]:
                        stop_loss = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[0], pos[1], pos[2], row.EURUSD_close)
                        # print(f'stop loss USDJPY = {stop_loss}')
                        eu_prof += stop_loss
                        losers += stop_loss
                        lose_count += 1
                        del eu_pos[idx]

            if len(uj_pos) > 0:
                for idx, pos in enumerate(uj_pos):
                    if row.USDJPY_close >= pos[6]:
                        # print(f'close trade {row.USDJPY_close} tp line = {pos[6]}')
                        take_profit = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[0], pos[1], pos[2], pos[6])
                        # print(f'take profit USDJPY = {take_profit}')
                        uj_prof += take_profit
                        winners += take_profit
                        win_count += 1
                        del uj_pos[idx]
                    elif row.USDJPY_close <= pos[5]:
                        stop_loss = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[0], pos[1], pos[2], row.USDJPY_close)
                        # print(f'stop loss USDJPY = {stop_loss}')
                        uj_prof += stop_loss
                        losers += stop_loss
                        lose_count += 1
                        del uj_pos[idx]

            # print(f'{row.time} running total = £{eu_prof + uj_prof}')
            results.append((row.time, eu_prof + uj_prof, eu_prof, uj_prof))
        print(f'Total = £{eu_prof + uj_prof} - winners = {winners} - losers = {losers} - win count = {win_count} - lose count = {lose_count}')
        results = pd.DataFrame(results, columns=['time', 'total', 'eurusd', 'usdjpy'])
        # plt.plot(results['total'])
        plt.plot(results['total'])
        plt.plot(results['eurusd'])
        plt.plot(results['usdjpy'])
        plt.show()


    def get_run_data(self):
        data = {}
        for symbol in self.symbols:
            symbol_data = []
            for date in pd.date_range(start=self.start, end=self.end, freq='D'):

                raw = pd.DataFrame(mt5.copy_rates_range(symbol, self.timeframe, date, date + timedelta(days=1)))
                raw = raw.rename(columns={'close': f'{symbol}_close', 'spread': f'{symbol}_spread'})
                raw = raw[['time', f'{symbol}_close', f'{symbol}_spread']]
                raw['time'] = pd.to_datetime(raw['time'], unit='s')
                # print(date, symbol, len(raw))
                symbol_data.append(raw)
            data[f'{symbol}'] = pd.concat(symbol_data)
        merged = data[list(data.keys())[0]].merge(data[list(data.keys())[1]], how='left', on='time')
        merged['time'] = pd.to_datetime(merged['time'], unit='s')
        merged = merged.drop_duplicates()
        merged = merged.ffill()
        self.data = merged




def run_backtest():
    mt5_connect_and_auth(strategy='demo_hedge_buy')
    start = datetime(year=2023, month=1, day=1)
    end = datetime(year=2024, month=2, day=28)
    timeframe = mt5.TIMEFRAME_M30
    symbols = ['EURUSD', 'USDJPY']
    HedgeEURUSDJPY_BUY(start, end, timeframe, symbols)




if __name__ == '__main__':
    run_backtest()
