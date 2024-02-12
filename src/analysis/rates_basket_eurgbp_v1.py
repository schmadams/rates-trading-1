from src.extractors.historical_extractor import HistoricalDataExtractor
from src.project_helper_functions.mt5_engine import mt5_connect_and_auth
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta


class RatesBasketEURGBPV1:
    data = {}

    def __init__(self, timeframe, start, end, strategy='demo_analysis'):
        mt5_connect_and_auth(strategy=strategy)
        self.timeframe = timeframe
        self.start, self.end = start, end
        self.run_extractors()
        self.ratio_analysis()
        self.parameters()
        self.first_test()

    def first_test(self):
        pos1, pos2, pos3 = None, None, None
        lot = 0.1
        total = 0
        for row in self.basket_df.itertuples():
            if row.ask_line <= self.bid_mean + (self.bid_std / 5) and pos1 == None:
                # print(row.time, row.ask_line, row.bid_line)
                pos1 = ('buy', row.gbpusd_ask, 'GBPUSD')
                pos2 = ('sell', row.eurusd_bid, 'EURUSD')
                pos3 = ('buy', row.eurgbp_ask, 'EURGBP')

            elif row.ask_line >= self.ask_mean - (self.ask_std / 5) and pos1 != None:
                p1_profit = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos1[2], lot, pos1[1], row.gbpusd_bid)
                p2_profit = mt5.order_calc_profit(mt5.ORDER_TYPE_SELL, pos2[2], lot, pos2[1], row.eurusd_ask)
                p3_profit = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos3[2], lot, pos3[1], row.eurgbp_bid)

                total += p1_profit + p2_profit + p3_profit
                pos1 = None
                pos2 = None
                pos3 = None


        print(self.start, self.end, total)
        self.profit = total

    def run_extractors(self):
        eurusd_class = HistoricalDataExtractor(symbol='EURUSD')
        self.data.update(
            {
                'eurusd': eurusd_class.get_ticks_from(start=self.start, end=self.end)
            }
        )

        gbpusd_class = HistoricalDataExtractor(symbol='GBPUSD')
        self.data.update(
            {
                'gbpusd': gbpusd_class.get_ticks_from(start=self.start, end=self.end)
            }
        )

        eg_class = HistoricalDataExtractor(symbol='EURGBP')
        self.data.update(
            {
                'eurgbp': eg_class.get_ticks_from(start=self.start, end=self.end)
            }
        )


    def parameters(self):
        self.bid_std = round(self.basket_df['bid_line'].std(), 5)
        self.ask_std = round(self.basket_df['ask_line'].std(), 5)

        self.bid_mean = round(self.basket_df['bid_line'].mean(), 5)
        self.ask_mean = round(self.basket_df['ask_line'].mean(), 5)

        self.buy_val = self.bid_mean + (self.bid_std / 4)
        self.sell_val = self.ask_mean - (self.ask_std / 4)


    def ratio_analysis(self):
        gu_df = self.data['gbpusd'].copy()
        eu_df = self.data['eurusd'].copy()
        eg_df = self.data['eurgbp'].copy()
        eu_df['eurusd_ask_inverted'] = 1/eu_df['eurusd_ask']
        eu_df['eurusd_bid_inverted'] = 1/eu_df['eurusd_bid']
        merged = pd.concat([eg_df, eu_df, gu_df]).sort_values('time')
        merged = merged.ffill().dropna().reset_index(drop=True)

        merged['ask_line'] = merged['eurusd_bid_inverted'] * merged['gbpusd_ask'] * merged['eurgbp_ask']
        merged['bid_line'] = merged['eurusd_ask_inverted'] * merged['gbpusd_bid'] * merged['eurgbp_bid']
        plot_df = merged[:]
        plt.plot(plot_df['ask_line'])
        plt.plot(plot_df['bid_line'], c='r')
        plt.show()

        self.basket_df = merged


if __name__ == '__main__':
    res = []
    for day in pd.date_range(start=pd.Timestamp('01-06-2023 00:00:00'), end=pd.Timestamp.now() - timedelta(days=1), freq='D'):
        prof = RatesBasketEURGBPV1(timeframe=mt5.TIMEFRAME_M1, start=str(day), end=str(day + timedelta(days=1))).profit
        res.append((day, prof))
    a=1
    a=1
