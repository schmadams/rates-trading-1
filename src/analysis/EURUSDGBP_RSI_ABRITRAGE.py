from datetime import datetime, timedelta
import MetaTrader5 as mt5
from src.project_helper_functions.mt5_engine import mt5_connect_and_auth
import pandas_ta as ta
import pandas as pd
import numpy as np


class RSIArbitrage:
    timeframe = mt5.TIMEFRAME_M1

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.get_data()
        self.get_rates_data()

    def get_data(self):
        rates = self.get_rates_data()
        ticks = self.loop_though_dates(rates)

    def loop_though_dates(self, rates):
        for date in rates['date'].unique():
            if pd.to_datetime(date) >= pd.to_datetime(self.start):
                print(date)
                day_ticks = self.get_ticks(date)
                day_rates = rates[rates['date'] == date]
                day_df = pd.concat([day_rates, day_ticks]).sort_values(by='time')
                self.day_test(day_df)


    def day_test(self, df):
        eu_pos, eg_pos, gu_pos = [], [], []
        for row in df.itertuples():
            if ~np.isnan(row.EURUSD_rsi):
                if row.EURUSD_rsi > 80 and row.EURGBP_rsi > 80 and row.GBPUSD < 80:
                    a=1
                    a=1



    def get_ticks(self, date):
        d1 = pd.to_datetime(date)
        d2 = pd.to_datetime(date) + timedelta(days=1)
        eu = self.clean_raw_ticks_data(mt5.copy_ticks_range('EURUSD', d1, d2, mt5.COPY_TICKS_ALL), prefix='EURUSD')
        eg = self.clean_raw_ticks_data(mt5.copy_ticks_range('EURGBP', d1, d2, mt5.COPY_TICKS_ALL), prefix='EURGBP')
        gu = self.clean_raw_ticks_data(mt5.copy_ticks_range('GBPUSD', d1, d2, mt5.COPY_TICKS_ALL), prefix='GBPUSD')
        ticks = pd.concat([eu, eg, gu]).sort_values(by='time').ffill().bfill()
        return ticks

    def clean_raw_ticks_data(self, df, prefix):
        df = pd.DataFrame(df)
        df = df[['bid', 'ask', 'time_msc']]
        df['time'] = pd.to_datetime(df['time_msc'], unit='ms')
        df = df.drop(columns=['time_msc'])

        for col in df.columns:
            if col != 'time':
                df = df.rename(columns={col: f'{prefix}_{col}'})
        return df

    def get_rates_data(self):
        eu = self.clean_raw_rates_data(mt5.copy_rates_range('EURUSD', self.timeframe,
                                                            self.start, self.end), prefix='EURUSD')
        eg = self.clean_raw_rates_data(mt5.copy_rates_range('EURGBP', self.timeframe,
                                                            self.start, self.end), prefix='EURGBP')
        gu = self.clean_raw_rates_data(mt5.copy_rates_range('GBPUSD', self.timeframe,
                                                            self.start, self.end), prefix='GBPUSD')

        final = eu.merge(eg, how='left', on='time').merge(gu, how='left', on='time')
        final['date'] = final['time'].dt.date
        return final


    def run_strategy(self):
        for date in set(self.data['time'].dt.date()):
            return None



    def clean_raw_rates_data(self, data, prefix):
        data = pd.DataFrame(data)
        data['time'] = pd.to_datetime(data['time'], unit='s')
        data = data[['time', 'close', 'spread']]
        for col in data.columns:
            if col != 'time':
                data = data.rename(columns={col: f'{prefix}_{col}'})
        data = self.rsi(data, prefix)
        return data

    def rsi(self, df, mkt, period=14):
        df[f'{mkt}_rsi'] = ta.rsi(df[f'{mkt}_close'], timeperiod=period)
        return df



if __name__ == '__main__':
    mt5_connect_and_auth(strategy='demo_rsi_eurusd')
    start = datetime(year=2024, month=5, day=1)
    end = datetime(year=2024, month=5, day=21)
    RSIArbitrage(start, end)