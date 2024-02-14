import warnings

# Ignore deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from src.project_helper_functions.mt5_engine import mt5_connect_and_auth
from src.project_helper_functions.mt5_executions import buy_order, sell_order, close_buy_order, close_sell_order
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta, datetime
import time
import pytz



class TriangleArb:
    def __init__(self, lot: float, deviation: list):
        self.lot = lot
        self.deviation = deviation
        self.get_signal_params()

    def get_signal_params(self):
        timezone = pytz.timezone("Etc/UTC")
        symbols = ['EURUSD', 'GBPUSD', 'EURGBP']
        start = datetime.now(tz=timezone) - timedelta(days=7)
        end = datetime.now(tz=timezone)

        raw_data = {symbol: [] for symbol in symbols}

        loop_ticks = []
        for i in range((end - start).days):
            d1 = start + (i * timedelta(days=1))
            d2 = d1 + timedelta(days=1)
            for symbol in symbols:
                ticks_raw = pd.DataFrame(mt5.copy_ticks_range(symbol, d1, d2, mt5.COPY_TICKS_ALL))
                ticks_raw = ticks_raw.rename(columns={'ask': f'{symbol.lower()}_ask', 'bid': f'{symbol.lower()}_bid'})
                ticks_raw = ticks_raw[['time', f'{symbol.lower()}_ask', f'{symbol.lower()}_bid']]
                raw_data[symbol].append(ticks_raw)

        eurusd_full = pd.concat(raw_data['EURUSD'])
        gbpusd_full = pd.concat(raw_data['GBPUSD'])
        eurgbp_full = pd.concat(raw_data['EURGBP'])

        eurusd_full['eurusd_ask_inverted'] = 1 / eurusd_full['eurusd_ask']
        eurusd_full['eurusd_bid_inverted'] = 1 / eurusd_full['eurusd_bid']
        basket_df = pd.concat([eurusd_full, gbpusd_full, eurgbp_full]).sort_values('time')
        basket_df['time'] = pd.to_datetime(basket_df['time'], unit='s')
        basket_df = basket_df.ffill().dropna().reset_index(drop=True)
        basket_df['ask_line'] = basket_df['eurusd_bid_inverted'] * basket_df['gbpusd_ask'] * basket_df['eurgbp_ask']
        basket_df['bid_line'] = basket_df['eurusd_ask_inverted'] * basket_df['gbpusd_bid'] * basket_df['eurgbp_bid']

        basket_df['day_time'] = basket_df['time'].dt.time

        basket_df = basket_df[(basket_df['day_time'] >= pd.to_datetime('09:00:00').time()) & (
                    basket_df['day_time'] <= pd.to_datetime('21:00:00').time())]

        self.ask_mean = basket_df['ask_line'].mean()
        self.bid_mean = basket_df['bid_line'].mean()
        self.ask_std = basket_df['ask_line'].std()
        self.bid_std = basket_df['bid_line'].std()
        print(f'ask_mean = {self.ask_mean} +- {self.ask_std}, bid_mean = {self.bid_mean} +- {self.bid_std}')

    def run_strategy(self):
        gu_pos, eu_pos, eg_pos = None, None, None
        open_level = (self.bid_mean + 3*(self.bid_std / 1))
        # close_level = (self.ask_mean - (self.ask_std / 1))
        close_level = 1.00008
        print(f'OPEN LEVEL = {round(open_level, 5)}'
              f' - CLOSE LEVEL = {round(close_level, 5)}')
        while True:
            eurusd = mt5.symbol_info_tick("EURUSD")
            gbpusd = mt5.symbol_info_tick('GBPUSD')
            eurgbp = mt5.symbol_info_tick("EURGBP")
            eu_ask, eu_bid = eurusd.ask, eurusd.bid
            gu_ask, gu_bid = gbpusd.ask, gbpusd.bid
            eg_ask, eg_bid = eurgbp.ask, eurgbp.bid


            if (1 / eu_bid * gu_ask * eg_ask) <= open_level and gu_pos == None and eu_pos == None and eg_pos == None:
                print(pd.Timestamp.now(), 'OPEN SIGNAL -- ', f'ask_line = {round(((1 / eu_bid) * gu_ask * eg_ask), 5)}'
                                              f' open level = {round(open_level, 5)}'
                                              f' close level = {round(close_level, 5)}')
                gu_pos = buy_order(symbol='GBPUSD', lot=self.lot, price=gu_ask, deviation=self.deviation)
                # print(f'trying to buy eurgbp at {eg_ask}')
                # eg_pos = buy_order(symbol='EURGBP', lot=self.lot, price=eg_ask, deviation=self.deviation)
                eu_pos = sell_order(symbol='EURUSD', lot=self.lot, price=eu_bid, deviation=self.deviation)

            if (1 / eu_bid * gu_ask * eg_ask) >= close_level and any(x != None for x in [gu_pos, eg_pos, eu_pos]):
                print(pd.Timestamp.now(), 'CLOSE SIGNAL -- ',
                      f'ask_line = {round((1 / eu_bid * gu_ask * eg_ask), 5)}'
                      f' open level = {round(open_level, 5)}'
                      f' close level = {round(close_level, 5)}', gu_pos, eu_pos)
                if gu_pos != None:
                    gu_pos = close_buy_order(symbol='GBPUSD', lot=self.lot, price=gu_bid, deviation=self.deviation, position=gu_pos)
                if eu_pos != None:
                    eu_pos = close_sell_order(symbol='EURUSD', lot=self.lot, price=eu_ask, deviation=self.deviation, position=eu_pos)
                if eg_pos != None:
                    eg_pos = close_buy_order(symbol='EURGBP', lot=self.lot, price=eg_bid, deviation=self.deviation, position=eg_pos)



if __name__ == '__main__':
    mt5_connect_and_auth(strategy='demo_triarb_v1')
    triarb = TriangleArb(lot=0.1, deviation=[0, 0])
    triarb.run_strategy()
