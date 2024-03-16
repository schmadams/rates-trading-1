import warnings

# Ignore deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

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


    def run_day(self, df, eu_pos=[], uj_pos=[]):
        lot, max_trades = 0.01, 100
        eu_pos, uj_pos = [], []
        eu_prof, uj_prof = 0, 0
        winners, losers = 0, 0
        win_count, lose_count = 0, 0
        sl, tp = 150, 2
        results = []
        for row in df.itertuples():
            if len(eu_pos) < max_trades and len(uj_pos) < max_trades:
                open_trade = ('EURUSD', lot, row.EURUSD_ask, row.time,
                              row.EURUSD_bid - sl*mt5.symbol_info('EURUSD').point,
                              row.EURUSD_ask + tp*mt5.symbol_info('EURUSD').point)
                eu_pos.append(open_trade)

                open_trade = ('USDJPY', lot, row.USDJPY_ask, row.time,
                              row.USDJPY_bid - sl*mt5.symbol_info('USDJPY').point,
                              row.USDJPY_ask + tp*mt5.symbol_info('USDJPY').point)
                uj_pos.append(open_trade)

            if len(eu_pos) > 0:
                for idx, pos in enumerate(eu_pos):
                    if row.EURUSD_bid >= pos[5]:
                        take_profit = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[0], pos[1], pos[2], pos[5])
                        # print(f'take profit = {take_profit}')
                        # print(f'take profit EURUSD = {take_profit}')
                        eu_prof += take_profit
                        winners += take_profit
                        win_count += 1
                        del eu_pos[idx]
                    elif row.EURUSD_bid <= pos[4]:
                        stop_loss = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[0], pos[1], pos[2], pos[4])
                        # print(f'stop loss EURUSD = {stop_loss}')
                        eu_prof += stop_loss
                        losers += stop_loss
                        lose_count += 1
                        del eu_pos[idx]

            if len(uj_pos) > 0:
                for idx, pos in enumerate(uj_pos):
                    if row.USDJPY_bid >= pos[5]:
                        take_profit = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[0], pos[1], pos[2], pos[5])
                        # print(f'take profit USDJPY = {take_profit}')
                        uj_prof += take_profit
                        winners += take_profit
                        win_count += 1
                        del uj_pos[idx]
                    elif row.USDJPY_bid <= pos[4]:
                        stop_loss = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[0], pos[1], pos[2], pos[4])
                        # print(f'stop loss USDJPY = {stop_loss}')
                        uj_prof += stop_loss
                        losers += stop_loss
                        lose_count += 1
                        del uj_pos[idx]

            results.append((row.time, eu_prof + uj_prof, eu_prof, uj_prof))

        if 0 not in [winners, win_count, losers, lose_count]:
            print(f'avg win = {winners / win_count} avg lose = {losers / lose_count} eurusd prof = {eu_prof} usdjpy = {uj_prof}')
        return eu_prof + uj_prof, eu_prof, uj_prof, winners, losers, eu_pos, uj_pos



    def get_run_data(self):
        run_total = 0
        eu_pos, uj_pos = [], []
        for date in pd.date_range(start=self.start, end=self.end, freq='D'):
            eu_ticks = self.tidy_raw_ticks('EURUSD', pd.DataFrame(mt5.copy_ticks_range('EURUSD', date, date + timedelta(days=1), mt5.COPY_TICKS_ALL)))
            uj_ticks =self.tidy_raw_ticks('USDJPY', pd.DataFrame(mt5.copy_ticks_range('USDJPY', date, date + timedelta(days=1), mt5.COPY_TICKS_ALL)))
            eu_rates = self.tidy_raw_rates('EURUSD', pd.DataFrame(mt5.copy_rates_range('EURUSD', mt5.TIMEFRAME_M1, date, date + timedelta(days=1))))
            uj_rates = self.tidy_raw_rates('USDJPY', pd.DataFrame(mt5.copy_rates_range('EURUSD', mt5.TIMEFRAME_M1, date, date + timedelta(days=1))))
            df = pd.concat([eu_ticks, uj_ticks]).sort_values(by='time')
            df = df.ffill()
            df = df.bfill()
            df = pd.concat([df, eu_rates, uj_rates]).sort_values(by='time')
            df['time'] = pd.to_datetime(df['time'], unit='s')
            total, eu_prof, uj_prof, wins, losses, eu_pos, uj_pos = self.run_day(df, eu_pos, uj_pos)
            run_total += total
            print(f'date = {date} running total = £{round(run_total, 2)} day total =£{round(total, 2)} wins={round(wins, 2)} losers ={round(losses, 2)}')

    def tidy_raw_rates(self, symbol, df):
        df = df.rename(columns={'close': f'{symbol}_close'})
        df = df[['time', f'{symbol}_close']]
        return df

    def tidy_raw_ticks(self, symbol, df):
        df = df.rename(columns={'ask': f'{symbol}_ask', 'bid': f'{symbol}_bid'})
        df = df[['time', f'{symbol}_ask', f'{symbol}_bid']]
        return df


def run_backtest():
    mt5_connect_and_auth(strategy='demo_hedge_buy')
    start = datetime(year=2023, month=10, day=1)
    end = datetime(year=2024, month=2, day=28)
    timeframe = mt5.TIMEFRAME_M1
    symbols = ['EURUSD', 'USDJPY']
    HedgeEURUSDJPY_BUY(start, end, timeframe, symbols)




if __name__ == '__main__':
    run_backtest()

    a=1
    a=1