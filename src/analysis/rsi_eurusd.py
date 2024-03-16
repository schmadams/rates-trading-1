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

class EURUSDRSIStrategy:
    period = 14
    positions = []

    def __init__(self, start, end, symbol, lot, timeframe):
        self.start, self.end, self.symbol = start, end, symbol
        self.lot, self.timeframe = lot, timeframe
        self.run_test()


    def run_test(self):
        final = []
        rates, ticks = self.get_day_data(self.start, self.end)
        # for date in pd.date_range(self.start, self.end, freq='D'):
        #     rates, ticks = self.get_day_data(date, date + timedelta(days=1))
        #     profit, trades = self.run_strategy(rates, ticks)
        #     print(date, profit, trades)
        #     final.append((date, profit, trades))
        # final = pd.DataFrame(final, columns=['date', 'profit', 'trades'])
        # print(final['profit'].sum(), final['profit'].mean())
        a=1
        a=1


    def run_strategy(self, rates, ticks):
        positions, total, trades = [], 0, 0
        rates['next_min'] = rates['time'].shift(-1)
        ticks['mid'] = ticks['ask'] - (ticks['ask'] - ticks['bid'])/2


        for rate_row in rates.itertuples():
            # print(rate_row.time, total)
            temp_ticks = ticks[(ticks['time'] >= rate_row.time) & (ticks['time'] < rate_row.next_min)]
            vals = rates[(rates['time'] > (rate_row.time - timedelta(minutes=13*5)))
                         & (rates['time'] < (rate_row.time))]['close']
            if len(vals) >= 12:
                for tick in temp_ticks.itertuples():
                    mid = tick.ask - (tick.ask - tick.bid)/2
                    rsi = self.calc_rsi_fly(vals, mid)

                    if rsi < 35 and len(positions) < 1:
                        positions.append((tick.time, 'buy', tick.ask))
                    elif rsi < 35 and len(positions) > 1 and len(positions) < 15:
                        if tick.time - positions[-1][0] > timedelta(minutes=1):
                            positions.append((tick.time, 'buy', tick.ask))

                    if rsi > 65:
                        for pos in positions:
                            profit = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, self.symbol, self.lot, pos[2], tick.bid)
                            trades += 1
                            total += profit
                        positions = []


        return total, trades

    def get_day_data(self, d1, d2):
        rates = pd.DataFrame(mt5.copy_rates_range(self.symbol, self.timeframe, d1, d2))
        ticks = pd.DataFrame(mt5.copy_ticks_range(self.symbol, d1, d2, mt5.COPY_TICKS_ALL))
        rates['time'] = pd.to_datetime(rates['time'], unit='s')
        ticks['time'] = pd.to_datetime(ticks['time_msc'], unit='ms')
        rates = rates[['time', 'open', 'close', 'high', 'low']]

        ticks = ticks[['time', 'bid', 'ask']]
        rates = self.calc_rsi_col(rates, self.period, d1, d2)
        rate_ticks = pd.concat([rates, ticks]).sort_values(by='time')
        rate_ticks['close'] = rate_ticks['close'].ffill()
        rate_ticks['mid'] = rate_ticks['ask'] - rate_ticks['bid']
        rate_ticks['tick_delta'] = rate_ticks['mid'] - rate_ticks['close']

        return rates, ticks

    def calc_rsi_fly(self, vals, mid):
        vals = pd.concat([vals, pd.Series([mid])], ignore_index=True)
        val_diff = vals.diff()

        gain = val_diff.clip(lower=0)
        loss = -val_diff.clip(upper=0)

        avg_gain = gain.mean()
        avg_loss = loss.mean()

        rs = avg_gain / avg_loss

        # Calculate the Relative Strength Index (RSI)
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calc_rsi_col(self, rates, period, d1, d2):
        # Calculate price changes
        rates['delta'] = rates['close'].diff()

        # Separate gains and losses
        rates['gain'] = rates['delta'].clip(lower=0)
        rates['loss'] = -rates['delta'].clip(upper=0)

        # Use EMA for average gains and losses
        rates['avg_gain'] = rates['gain'].ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
        rates['avg_loss'] = rates['loss'].ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

        # Avoid division by zero and calculate RS and RSI
        rates['rs'] = rates['avg_gain'] / rates['avg_loss']
        rates['rsi_manual'] = 100 - (100 / (1 + rates['rs']))

        # Calculate RSI using TA-Lib for comparison
        rates['proper_rsi'] = ta.rsi(rates['close'], timeperiod=period)

        return rates


if __name__ == '__main__':
    mt5_connect_and_auth(strategy='demo_rsi_eurusd')
    EURUSDRSIStrategy(
        start=datetime(year=2024,  month=1, day=1),
        end=datetime(year=2024, month=3, day=14),
        symbol='EURUSD',
        lot=0.01,
        timeframe=mt5.TIMEFRAME_M5
    )