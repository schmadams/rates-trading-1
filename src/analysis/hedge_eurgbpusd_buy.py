import warnings

# Ignore deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import MetaTrader5 as mt5
import pandas as pd

from src.project_helper_functions.mt5_engine import mt5_connect_and_auth
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
class tripbuy_eurusdgbp:
    def __init__(self, run_start, run_end, timeframe, symbols, lot):
        self.lot = lot
        self.start = run_start
        self.timeframe = timeframe
        self.end = run_end
        self.symbols = symbols
        self.get_run_data()

    def get_symbol_day_rates(self, symbol, day):
        data = pd.DataFrame(mt5.copy_rates_range(symbol, self.timeframe, day, day + timedelta(days=1)))
        data['time'] = pd.to_datetime(data['time'], unit='s')
        data = data[['time', f'close',f'high', f'low', f'open', f'spread']].rename(columns={
            'close': f'{symbol}_close',
            'high': f'{symbol}_high',
            'low': f'{symbol}_low',
            'open': f'{symbol}_open',
            'spread': f'{symbol}_spread'})
        # print(symbol, data.shape)
        return data

    def tidy_date_data(self, df):
        df = df.groupby('time').max().reset_index()
        df = df.sort_values(by='time')
        return df

    def symbol_profit(self, symbol, data):
        data[f'{symbol}_final'] = [open - (mt5.symbol_info(symbol).point*1.5*spread) / 2
                                   if low < open - (mt5.symbol_info(symbol).point*1.5*spread) / 2
                                   else open + (mt5.symbol_info(symbol).point * spread * 10) if open + (mt5.symbol_info(symbol).point * spread * 10) < high
                                   else close - mt5.symbol_info(symbol).point * spread
                                   for low, close, open, spread, high
                                   in zip(data[f'{symbol}_low'],
                                          data[f'{symbol}_close'],
                                          data[f'{symbol}_open'],
                                          data[f'{symbol}_spread'],
                                          data[f'{symbol}_high'])]
        profit = []
        data[f'{symbol}_delta'] = data[f'{symbol}_final'] - data[f'{symbol}_open']
        for open, close in zip(data[f'{symbol}_open'], data[f'{symbol}_final']):
            profit.append(mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, symbol, self.lot, open, close))
        data[f'{symbol}_profit'] = profit
        return data

    def get_run_data(self):
        final = []
        for date in pd.date_range(start=self.start, end=self.end, freq='D'):
            run_data = self.tidy_date_data(pd.concat([self.get_symbol_day_rates(x, date)
                                                      for x in self.symbols]).sort_values(by='time'))
            for symbol in self.symbols:
                run_data = self.symbol_profit(symbol, run_data)

            final.append(run_data)
            print(date, round(run_data['EURUSD_profit'].sum(), 2), round(run_data['GBPUSD_profit'].sum(), 2),
                  round(run_data['EURGBP_profit'].sum(), 2))
        final = pd.concat(final)
        print(final['EURUSD_profit'].sum(), final['GBPUSD_profit'].sum(), final['EURGBP_profit'].sum())





def run_backtest():
    mt5_connect_and_auth(strategy='demo_hedge_buy')
    start = datetime(year=2023, month=10, day=11)
    end = datetime(year=2024, month=2, day=28)
    timeframe = mt5.TIMEFRAME_H1
    symbols = ['EURUSD', 'EURGBP', 'GBPUSD']
    tripbuy_eurusdgbp(start, end, timeframe, symbols, lot=0.05)




if __name__ == '__main__':
    run_backtest()
