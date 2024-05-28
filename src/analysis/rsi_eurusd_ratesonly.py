import warnings

# Ignore deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import MetaTrader5 as mt5
import statistics
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.project_helper_functions.mt5_engine import mt5_connect_and_auth
import pandas_ta as ta
import matplotlib.pyplot as plt

class EURUSDRSIStrategy:
    period = 14
    positions = []

    def __init__(self, start, end, symbol, lot, timeframe, max_trades, trade_break):
        self.start, self.end, self.symbol = start, end, symbol
        self.lot, self.timeframe = lot, timeframe
        self.max_trades = max_trades
        self.trade_break = trade_break
        self.point = mt5.symbol_info(self.symbol).point
        self.run_test()


    def run_test(self):
        positions, final_profit, final_wins, final_losses, total_trades = [], 0, 0, 0, 0
        for date in pd.date_range(self.start, self.end):
            rates = self.get_day_data(date, date + timedelta(days=1))
        #     positions, profit, win, loss, num_trades = self.run_strategy(rates, positions)
        #     if len(rates) > 0:
        #         positions, total, wins, loss, num_trades = self.run_strategy(rates, positions)
        #         final_profit += total
        #         final_wins += wins
        #         final_losses += loss
        #         total_trades += num_trades
        #         print(date, total, wins, loss, num_trades)
        # print(f'Overall -- Profit=£{final_profit} -- Wins=£{final_wins} -- Losses={final_losses} -- Total Trades={total_trades}')

        return rates

    def create_plot(self, rates):
        fig, ax1 = plt.subplots()  # Creates the figure and the first y-axis

        color = 'tab:red'
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Close', color=color)  # First y-axis label
        ax1.plot(rates['time'], rates['close'], color=color)  # Plotting the 'close' data
        ax1.tick_params(axis='y', labelcolor=color)

        ax2 = ax1.twinx()  # Instantiate a second y-axis that shares the same x-axis

        color = 'tab:blue'
        ax2.set_ylabel('RSI', color=color)  # Second y-axis label
        # Assuming you've converted 'rsi_5' list of lists into a Series or similar structure suitable for plotting.
        # If 'rsi_5' still contains None or is not properly calculated, you'll need to fix that first.
        ax2.plot(rates['time'], rates['rsi_5'], color=color)  # Plotting the 'rsi_5' data
        ax2.tick_params(axis='y', labelcolor=color)

        fig.tight_layout()  # Adjust layout to make room for the second y-axis label
        plt.show()

    def open_positions(self, positions, row):
        positions.append((row.time, row.close,
                                      row.close - 100*row.spread*self.point,
                                      row.close + 250*row.spread*self.point))
        return positions

    def close_trade(self, profit, win, loss, num_trades, pos, row, sl=False, tp=False):
        if sl:
            trade_prof = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, self.symbol,
                                               self.lot, pos[1], pos[2])
        elif tp:
            trade_prof = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, self.symbol,
                                               self.lot, pos[1], pos[3])
        else:
            trade_prof = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, self.symbol,
                                           self.lot, pos[1], row.close - row.spread * self.point)
        if trade_prof > 0:
            win += trade_prof
        else:
            loss += trade_prof
        profit += trade_prof
        num_trades += 1

        return profit, win, loss, num_trades


    def run_strategy(self, df, positions=[]):
        remove_pos = []
        win, loss, profit, num_trades = 0, 0, 0, 0
        for row in df.itertuples():
            if row.rsi_15 is not None:
                if row.rsi_15 < 35 and len(positions) < self.max_trades:
                    positions = self.open_positions(positions, row)

                if row.rsi_15 > 65:
                    remove_pos = []
                    for pos in positions:
                        profit, win, loss, num_trades = self.close_trade(profit, win, loss, num_trades, pos, row)
                        remove_pos.append(pos)






            # if row.rsi_1 < 30:
            #     if len(positions) < 1:
            #         positions = self.open_positions(positions, row)
            #     elif len(positions) < self.max_trades and row.time - positions[-1][0] > timedelta(minutes=self.trade_break):
            #         positions = self.open_positions(positions, row)
            #
            # if row.rsi_1 > 70 or row.rsi_5 > 60:
            #     remove_pos = []
            #     for pos in positions:
            #         profit, win, loss, num_trades = self.close_trade(profit, win, loss, num_trades, pos, row)
            #         remove_pos.append(pos)
            #
            # for pos in positions:
            #     if pos not in remove_pos:
            #         if row.low < pos[2]:
            #             profit, win, loss, num_trades = self.close_trade(profit, win, loss, num_trades, pos, row, sl=True)
            #             remove_pos.append(pos)
            #
            #         elif row.high > pos[3]:
            #             profit, win, loss, num_trades = self.close_trade(profit, win, loss, num_trades, pos, row, tp=True)
            #             remove_pos.append(pos)

            for pos in remove_pos:
                positions.remove(pos)
            remove_pos = []



        return positions, profit, win, loss, num_trades

    def interval_rsi(self, i):


    def get_day_data(self, d1, d2):
        df1 = self.fix_rates(mt5.copy_rates_range(self.symbol, self.timeframe, d1, d2), prefix='1')
        df5 = self.fix_rates(mt5.copy_rates_range(self.symbol, mt5.TIMEFRAME_M5, d1, d2), prefix='5')
        df5['rsi_true'] = ta.rsi(df5['5_close'], length=14)
        df = df1.merge(df5, how='left', on='time')

        rsi_5 = []
        for idx, val in enumerate(df['1_close']):
            for i in [5, 15]:
            m_vals = [df['5_close'][x] for x in range(0, idx+1, 1)
                      if x>=0 and df['5_close'][x] is not None and
                      str(df['5_close'][x]) != 'nan']
            if str(df['5_close'][idx]) == 'nan':
                m_vals.append(val)
            rsi = ta.rsi(pd.Series(m_vals), length=14)
            if rsi is not None:
                rsi = rsi.iloc[-1]
            rsi_5.append(rsi)
        df['rsi_5'] = rsi_5

        df = df.reset_index()
        return df

    def fix_rates(self, data, prefix):
        data = pd.DataFrame(data)
        data['time'] = pd.to_datetime(data['time'], unit='s')
        for col in data.columns:
            if col != 'time':
                data = data.rename(columns={col: f'{prefix}_{col}'})
        return data





if __name__ == '__main__':
    mt5_connect_and_auth(strategy='demo_rsi_eurusd')
    EURUSDRSIStrategy(
        start=datetime(year=2024,  month=3, day=20),
        end=datetime(year=2024, month=3, day=21),
        symbol='EURUSD',
        lot=0.01,
        timeframe=mt5.TIMEFRAME_M1,
        max_trades=15,
        trade_break=1
    )