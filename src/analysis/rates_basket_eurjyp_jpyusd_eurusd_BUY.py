from src.extractors.historical_extractor import HistoricalDataExtractor
from src.project_helper_functions.mt5_engine import mt5_connect_and_auth
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta, datetime
import pytz



class RatesBasketEURUSDJPY_BUY:
    data = {}

    def __init__(self, timeframe, start, end):
        self.timeframe = timeframe
        self.start, self.end = start, end
        self.run_extractors()
        self.ratio_analysis()
        self.parameters()

    def first_test(self):
        pos1, pos2, pos3 = [], [], []
        stop_loss = 0.1
        trade_limit = 50
        lot1, lot2, lot3, lot4, total, winners, losers = 0.1, 0.2, 0.3, 0.4, 0, 0, 0
        eurusd_prof, usdjpy_prof, eurjpy_prof, num_trades = 0, 0, 0, 0
        # close_level = self.ask_mean + 1*self.ask_std
        close_level = self.bid_mean
        # open_level_1 =
        open_level_1 = self.bid_mean
        open_level_2 = self.bid_mean - 1*self.bid_std
        open_level_3 = self.bid_mean - 2*self.bid_std
        print(self.ask_mean, open_level_1, open_level_2, open_level_3)
        for row in self.basket_df.itertuples():
            for idx, pos in enumerate(pos1):
                if row.usdjpy_bid <= pos[1] - stop_loss:
                    total += mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[2], pos[3], pos[1], row.usdjpy_bid)
                    usdjpy_prof += mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[2], pos[3], pos[1], row.usdjpy_bid)
                    del pos1[idx]

            for idx, pos in enumerate(pos2):
                if row.eurusd_bid <= pos[1] - stop_loss:
                    total += mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[2], pos[3], pos[1], row.eurusd_bid)
                    eurusd_prof += mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[2], pos[3], pos[1], row.eurusd_bid)
                    del pos2[idx]

            for idx, pos in enumerate(pos3):
                if row.eurjpy_ask >= pos[1] + stop_loss:
                    total += mt5.order_calc_profit(mt5.ORDER_TYPE_SELL, pos[2], pos[3], pos[1], row.eurjpy_ask)
                    eurjpy_prof += mt5.order_calc_profit(mt5.ORDER_TYPE_SELL, pos[2], pos[3], pos[1], row.eurjpy_ask)
                    del pos3[idx]


            if row.ask_line <= open_level_1 and row.ask_line > open_level_2:
                if len(pos1) < trade_limit:
                    pos1.append(('buy', row.usdjpy_ask, 'USDJPY', lot1))
                if len(pos2) < trade_limit:
                    pos2.append(('buy', row.eurusd_ask, 'EURUSD', lot1))
                if len(pos3) < trade_limit:
                    pos3.append(('sell', row.eurjpy_bid, 'EURJPY', lot1))

            elif row.ask_line <= open_level_2 and row.ask_line > open_level_3:
                if len(pos1) < trade_limit:
                    pos1.append(('buy', row.usdjpy_ask, 'USDJPY', lot2))
                if len(pos2) < trade_limit:
                    pos2.append(('buy', row.eurusd_ask, 'EURUSD', lot2))
                if len(pos3) < trade_limit:
                    pos3.append(('sell', row.eurjpy_bid, 'EURJPY', lot2))

            elif row.ask_line <= open_level_3:
                if len(pos1) < trade_limit:
                    pos1.append(('buy', row.usdjpy_ask, 'USDJPY', lot3))
                if len(pos2) < trade_limit:
                    pos2.append(('buy', row.eurusd_ask, 'EURUSD', lot3))
                if len(pos3) < trade_limit:
                    pos3.append(('sell', row.eurjpy_bid, 'EURJPY', lot3))

            # elif row.ask_line <= open_level_4:
            #     if len(pos1) < trade_limit:
            #         pos1.append(('buy', row.usdjpy_ask, 'USDJPY', lot4))
            #     if len(pos2) < trade_limit:
            #         pos2.append(('buy', row.eurusd_ask, 'EURUSD', lot4))
            #     if len(pos3) < trade_limit:
            #         pos3.append(('sell', row.eurjpy_bid, 'EURJPY', lot4))


            if row.bid_line >= close_level:
                for idx, pos in enumerate(pos1):
                    trade_prof = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[2], pos[3], pos[1], row.usdjpy_bid)
                    # print(f'closing {pos[2]} trade open ask = {pos[1]} close bid = {row.usdjpy_bid} close ask = {row.usdjpy_ask}')
                    total += trade_prof
                    usdjpy_prof += trade_prof
                    num_trades += 1
                    del pos1[idx], trade_prof

                for idx, pos in enumerate(pos2):
                    trade_prof = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[2], pos[3], pos[1], row.eurusd_bid)
                    total += trade_prof
                    eurusd_prof += trade_prof
                    num_trades += 1
                    del pos2[idx], trade_prof

                for idx, pos in enumerate(pos3):
                    trade_prof = mt5.order_calc_profit(mt5.ORDER_TYPE_SELL, pos[2], pos[3], pos[1], row.eurjpy_ask)
                    # print(f'Closing {pos[2]} {pos[0]} position open price = {pos[1]} close price = {row.eurjpy_ask}')
                    total += trade_prof
                    eurjpy_prof += trade_prof
                    num_trades += 1
                    del pos3[idx], trade_prof


        print(self.start, self.end, int(total), num_trades)
        return total, eurusd_prof, usdjpy_prof, eurjpy_prof, num_trades

    def run_extractors(self):
        eurusd_class = HistoricalDataExtractor(symbol='EURUSD')
        self.data.update(
            {
                'eurusd': eurusd_class.get_ticks_range(start=self.start, end=self.end)
            }
        )

        gbpusd_class = HistoricalDataExtractor(symbol='USDJPY')
        self.data.update(
            {
                'usdjpy': gbpusd_class.get_ticks_range(start=self.start, end=self.end)
            }
        )

        eg_class = HistoricalDataExtractor(symbol='EURJPY') # this one is gonna be inverted
        self.data.update(
            {
                'eurjpy': eg_class.get_ticks_range(start=self.start, end=self.end)
            }
        )


    def parameters(self):
        self.bid_std = round(self.basket_df['bid_line'].std(), 5)
        self.ask_std = round(self.basket_df['ask_line'].std(), 5)

        self.bid_mean = round(self.basket_df['bid_line'].mean(), 5)
        self.ask_mean = round(self.basket_df['ask_line'].mean(), 5)


    def ratio_analysis(self):
        uj_df = self.data['usdjpy'].copy()
        eu_df = self.data['eurusd'].copy()
        ej_df = self.data['eurjpy'].copy()
        ej_df['jpyeur_bid'] = 1/ej_df['eurjpy_ask']
        ej_df['jpyeur_ask'] = 1/ej_df['eurjpy_bid']
        merged = pd.concat([uj_df, eu_df, ej_df]).sort_values('time')
        merged = merged.ffill().dropna().reset_index(drop=True)
        merged['ask_line'] = merged['jpyeur_ask'] * merged['usdjpy_ask'] * merged['eurusd_ask']
        merged['bid_line'] = merged['jpyeur_bid'] * merged['usdjpy_bid'] * merged['eurusd_bid']

        # plt.plot(merged['ask_line'])
        # plt.plot(merged['bid_line'], c='r')
        # plt.show()

        merged['usdjpy_spread'] = merged['usdjpy_ask'] - merged['usdjpy_bid']
        merged['eurusd_spread'] = merged['eurusd_ask'] - merged['eurusd_bid']
        merged['eurjpy_spread'] = merged['eurjpy_ask'] - merged['eurjpy_bid']

        self.basket_df = merged


if __name__ == '__main__':
    mt5_connect_and_auth(strategy='demo_triarb_v1')
    timezone = pytz.timezone("Etc/UTC")

    res = []

    start = datetime(year=2023, month=1, day=1, tzinfo=timezone)
    end = datetime(year=2024, month=2, day=24, tzinfo=timezone)

    for i in range((end-start).days):
        d1 = start + (i * timedelta(days=1))
        d2 = d1 + timedelta(days=1)
        d1 = d1.strftime('%d-%m-%Y %H:%M:%S')
        d2 = d2.strftime('%d-%m-%Y %H:%M:%S')
        prof, eurusd_prof, usdjpy_prof, eurjpy_prof, num_trades = RatesBasketEURUSDJPY_BUY(timeframe=mt5.TIMEFRAME_M1, start=d1, end=d2).first_test()
        res.append((d1, prof, eurusd_prof, usdjpy_prof, eurjpy_prof, num_trades))
        print('running total', round(sum([x[1] for x in res]), 2))
    res = pd.DataFrame(res, columns=['date', 'profit', 'eurusd_prof', 'usdjpy_prof', 'eurjpy_prof' , 'trades'])
    res['pnl'] = res['profit'].cumsum()
    plt.plot(res['pnl'])
    plt.show()

    print(res['profit'].sum(), res['profit'].mean(), res['eurusd_prof'].sum(),
          res['usdjpy_prof'].sum(), res['eurjpy_prof'].sum(), res['trades'].mean())
    a=1
    a=1
