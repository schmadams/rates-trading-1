from src.extractors.historical_extractor import HistoricalDataExtractor
from src.project_helper_functions.mt5_engine import mt5_connect_and_auth
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta, datetime
import pytz



class RatesBasketEURUSDGBPUSDEURGBP:
    data = {}

    def __init__(self, timeframe, start, end):
        self.timeframe = timeframe
        self.start, self.end = start, end
        self.run_extractors()
        self.ratio_analysis()
        self.parameters()

    def first_test(self):
        pos1, pos2 = [], []
        stop_loss, sl, tp = 0.002, 1.5, 1
        trade_limit = 5
        lot1, lot2, lot3, lot4, total, winners, losers = 0.01, 0.02, 0.03, 0.04, 0, 0, 0
        eurusd_prof, gbpusd_prof, num_trades = 0, 0, 0
        # close_level = self.ask_mean + self.ask_std
        open_level_1 = self.ask_mean - (self.ask_mean - self.bid_mean)/4
        open_level_2 = self.bid_mean + self.bid_std
        open_level_3 = self.bid_mean
        open_level_4 = self.bid_mean - self.bid_std
        print(self.ask_mean, open_level_1, open_level_2, open_level_3)
        for row in self.basket_df.itertuples():
            for idx, pos in enumerate(pos1):
                if row.gbpusd_bid <= pos[-2]:
                    total += mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[2], pos[3], pos[1], pos[-2])
                    gbpusd_prof += mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[2], pos[3], pos[1], pos[-2])
                    # print(f'stop loss with profit of '
                    #       f'{mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[2], pos[3], pos[1], row.gbpusd_bid)}')
                    del pos1[idx]

            for idx, pos in enumerate(pos2):
                if row.eurusd_ask >= pos[-2]:
                    total += mt5.order_calc_profit(mt5.ORDER_TYPE_SELL, pos[2], pos[3], pos[1], pos[-2])
                    eurusd_prof += mt5.order_calc_profit(mt5.ORDER_TYPE_SELL, pos[2], pos[3], pos[1], pos[-2])
                    del pos2[idx]


            if row.ask_line <= open_level_1 and row.ask_line > open_level_2:
                if len(pos1) < trade_limit:
                    pos1.append(('buy', row.gbpusd_ask, 'GBPUSD', lot1, row.time,
                                 row.gbpusd_bid - sl*mt5.symbol_info('GBPUSD').point,
                                 row.gbpusd_ask + tp*mt5.symbol_info('GBPUSD').point))
                if len(pos2) < trade_limit:
                    pos2.append(('sell', row.eurusd_bid, 'EURUSD', lot1, row.time,
                                 row.gbpusd_bid + sl*mt5.symbol_info('EURUSD').point,
                                 row.gbpusd_ask - tp*mt5.symbol_info('EURUSD').point))

            elif row.ask_line <= open_level_2 and row.ask_line > open_level_3:
                if len(pos1) < trade_limit:
                    pos1.append(('buy', row.gbpusd_ask, 'GBPUSD', lot2, row.time,
                                 row.gbpusd_bid - sl*mt5.symbol_info('GBPUSD').point,
                                 row.gbpusd_ask + tp*mt5.symbol_info('GBPUSD').point))
                if len(pos2) < trade_limit:
                    pos2.append(('sell', row.eurusd_bid, 'EURUSD', lot2, row.time,
                                 row.gbpusd_bid + sl*mt5.symbol_info('EURUSD').point,
                                 row.gbpusd_ask - tp*mt5.symbol_info('EURUSD').point))

            elif row.ask_line <= open_level_3 and row.ask_line > open_level_4:
                if len(pos1) < trade_limit:
                    pos1.append(('buy', row.gbpusd_ask, 'GBPUSD', lot3, row.time,
                                 row.gbpusd_bid - sl*mt5.symbol_info('GBPUSD').point,
                                 row.gbpusd_ask + tp*mt5.symbol_info('GBPUSD').point))
                if len(pos2) < trade_limit:
                    pos2.append(('sell', row.eurusd_bid, 'EURUSD', lot3, row.time,
                                 row.gbpusd_bid + sl*mt5.symbol_info('EURUSD').point,
                                 row.gbpusd_ask - tp*mt5.symbol_info('EURUSD').point))

            elif row.ask_line <= open_level_4:
                if len(pos1) < trade_limit:
                    pos1.append(('buy', row.gbpusd_ask, 'GBPUSD', lot4, row.time,
                                 row.gbpusd_bid - sl*mt5.symbol_info('GBPUSD').point,
                                 row.gbpusd_ask + tp*mt5.symbol_info('GBPUSD').point))
                if len(pos2) < trade_limit:
                    pos2.append(('sell', row.eurusd_bid, 'EURUSD', lot4, row.time,
                                 row.gbpusd_bid + sl*mt5.symbol_info('EURUSD').point,
                                 row.gbpusd_ask - tp*mt5.symbol_info('EURUSD').point))


            # if row.ask_line >= close_level:
            # if row.bid_line >= self.bid_mean + self.bid_std:
            for idx, pos in enumerate(pos1):
                if row.gbpusd_bid >= pos[-1]:
                    trade_prof = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[2], pos[3], pos[1], row.gbpusd_bid)
                    total += trade_prof
                    # print(f'close buy - trade open = {pos[4]} trade close = {row.time} volumne = {pos[3]}')
                    gbpusd_prof += trade_prof
                    num_trades += 1
                    del pos1[idx], trade_prof

            for idx, pos in enumerate(pos2):
                if row.eurusd_ask <= pos[-1]:
                    trade_prof = mt5.order_calc_profit(mt5.ORDER_TYPE_SELL, pos[2], pos[3], pos[1], row.eurusd_ask)
                    # print(f'close buy - trade open = {pos[4]} trade close = {row.time} volumne = {pos[3]}')
                    total += trade_prof
                    eurusd_prof += trade_prof
                    num_trades += 1
                    del pos2[idx], trade_prof

            if total < -1000:
                for idx, pos in enumerate(pos1):
                    total += mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[2], pos[3], pos[1], row.gbpusd_bid)
                    gbpusd_prof += mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, pos[2], pos[3], pos[1], row.gbpusd_bid)
                    del pos1[idx]

                for idx, pos in enumerate(pos2):
                    total += mt5.order_calc_profit(mt5.ORDER_TYPE_SELL, pos[2], pos[3], pos[1], row.eurusd_ask)
                    eurusd_prof += mt5.order_calc_profit(mt5.ORDER_TYPE_SELL, pos[2], pos[3], pos[1], row.eurusd_ask)
                    del pos2[idx]
                break

        print(self.start, self.end, int(total), num_trades)
        print(f'EURUSD PROFIT = {eurusd_prof} and GBPUSD PROFIT = {gbpusd_prof} ')
        return total, eurusd_prof, gbpusd_prof, num_trades

    def run_extractors(self):
        eurusd_class = HistoricalDataExtractor(symbol='EURUSD')
        self.data.update(
            {
                'eurusd': eurusd_class.get_ticks_range(start=self.start, end=self.end)
            }
        )

        gbpusd_class = HistoricalDataExtractor(symbol='GBPUSD')
        self.data.update(
            {
                'gbpusd': gbpusd_class.get_ticks_range(start=self.start, end=self.end)
            }
        )

        eg_class = HistoricalDataExtractor(symbol='EURGBP')
        self.data.update(
            {
                'eurgbp': eg_class.get_ticks_range(start=self.start, end=self.end)
            }
        )


    def parameters(self):
        self.bid_std = round(self.basket_df['bid_line'].std(), 5)
        self.ask_std = round(self.basket_df['ask_line'].std(), 5)

        self.bid_mean = round(self.basket_df['bid_line'].mean(), 5)
        self.ask_mean = round(self.basket_df['ask_line'].mean(), 5)

    def ratio_analysis(self):
        gu_df = self.data['gbpusd'].copy()
        eu_df = self.data['eurusd'].copy()
        eg_df = self.data['eurgbp'].copy()
        eu_df['eurusd_ask_inverted'] = 1/eu_df['eurusd_ask']
        eu_df['eurusd_bid_inverted'] = 1/eu_df['eurusd_bid']
        merged = pd.concat([eg_df, eu_df]).sort_values('time')
        merged = pd.concat([merged, gu_df]).sort_values('time')
        # merged = pd.concat([eg_df, eu_df, gu_df]).sort_values('time')
        merged = merged.groupby('time').max().reset_index()
        merged = merged.ffill().bfill().reset_index(drop=True)
        merged['ask_line'] = merged['eurusd_bid_inverted'] * merged['gbpusd_ask'] * merged['eurgbp_ask']
        merged['bid_line'] = merged['eurusd_ask_inverted'] * merged['gbpusd_bid'] * merged['eurgbp_bid']
        self.basket_df = merged


if __name__ == '__main__':
    mt5_connect_and_auth(strategy='demo_triarb_v1')
    timezone = pytz.timezone("Etc/UTC")

    res = []

    start = datetime(year=2024, month=1, day=1, tzinfo=timezone)
    end = datetime(year=2024, month=3, day=2, tzinfo=timezone)

    for i in range((end-start).days):
        d1 = start + (i * timedelta(days=1))
        d2 = d1 + timedelta(days=1)
        d1 = d1.strftime('%d-%m-%Y %H:%M:%S')
        d2 = d2.strftime('%d-%m-%Y %H:%M:%S')
        prof, eurusd_prof, gbpusd_prof, num_trades = RatesBasketEURUSDGBPUSDEURGBP(timeframe=mt5.TIMEFRAME_M1, start=d1, end=d2).first_test()
        res.append((d1, prof, eurusd_prof, gbpusd_prof, num_trades))
        print('running total', round(sum([x[1] for x in res]), 2))
    res = pd.DataFrame(res, columns=['date', 'profit', 'eurusd', 'gbpusd', 'trades'])
    res['pnl'] = res['profit'].cumsum()
    plt.plot(res['pnl'])
    plt.show()

    print(res['profit'].sum(), res['profit'].mean(), res['eurusd'].sum(), res['gbpusd'].sum(), res['trades'].mean())
    a=1
    a=1
