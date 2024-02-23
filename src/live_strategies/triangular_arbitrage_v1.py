import warnings

# Ignore deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from src.project_helper_functions.mt5_engine import mt5_connect_and_auth
from src.project_helper_functions.mt5_executions import buy_order, sell_order, close_buy_order, close_sell_order
import MetaTrader5 as mt5
import pandas as pd
from datetime import timedelta, datetime
import pytz
import logging


current_time = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')

# Configure logging to write to a file, with the desired log level and format including the current time
logging.basicConfig(filename='../logs/run_{}.log'.format(current_time), filemode='w',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)


class TriangleArb:
    def __init__(self, lot: float, deviation: list, stop_loss: float):
        self.lot1 = lot
        self.lot2 = lot * 2
        self.lot3 = lot * 3
        self.lot4 = lot * 4
        self.stop_loss = stop_loss
        self.deviation = deviation

    def get_bid_ask_stats(self):
        timezone = pytz.timezone("Etc/UTC")
        symbols = ['EURUSD', 'GBPUSD', 'EURGBP']
        start = datetime.now(tz=timezone) - timedelta(minutes=20)
        end = datetime.now(tz=timezone)

        raw_data = {symbol: [] for symbol in symbols}

        for symbol in symbols:
            ticks_raw = pd.DataFrame(mt5.copy_ticks_range(symbol, start, end, mt5.COPY_TICKS_ALL))
            ticks_raw = ticks_raw.rename(columns={'ask': f'{symbol.lower()}_ask', 'bid': f'{symbol.lower()}_bid'})
            ticks_raw = ticks_raw[['time', f'{symbol.lower()}_ask', f'{symbol.lower()}_bid']]
            raw_data[symbol].append(ticks_raw)

        eurusd_full = pd.concat(raw_data['EURUSD'])
        gbpusd_full = pd.concat(raw_data['GBPUSD'])
        eurgbp_full = pd.concat(raw_data['EURGBP'])

        basket_df = pd.concat([eurusd_full, gbpusd_full, eurgbp_full]).sort_values('time')
        basket_df['time'] = pd.to_datetime(basket_df['time'], unit='s')
        basket_df = basket_df.ffill().dropna().reset_index(drop=True)
        basket_df['ask_line'] = (1 / basket_df['eurusd_bid']) * basket_df['gbpusd_ask'] * basket_df['eurgbp_ask']
        basket_df['bid_line'] = (1 / basket_df['eurusd_ask']) * basket_df['gbpusd_bid'] * basket_df['eurgbp_bid']
        return basket_df['ask_line'].mean(), basket_df['bid_line'].mean(),\
            basket_df['ask_line'].std(), basket_df['bid_line'].std()

    def open_close_levels(self):
        ask_mean, bid_mean, ask_std, bid_std = self.get_bid_ask_stats()
        print(ask_mean, bid_mean, ask_std, bid_std)
        close_level = ask_mean + ask_std
        open_level_1 = ask_mean - (ask_mean - bid_mean) / 2
        # open_level_1 = ask_mean
        open_level_2 = bid_mean + bid_std
        open_level_3 = bid_mean
        open_level_4 = bid_mean - bid_std
        return close_level, open_level_1, open_level_2, open_level_3, open_level_4, pd.Timestamp.now()

    def get_positions(self):
        eurusd_pos = [pos for pos in mt5.positions_get(symbol="EURUSD")]
        gbpusd_pos = [pos for pos in mt5.positions_get(symbol="GBPUSD")]
        return eurusd_pos, gbpusd_pos

    def get_live_ticks(self):
        eurusd = mt5.symbol_info_tick("EURUSD")
        gbpusd = mt5.symbol_info_tick('GBPUSD')
        eurgbp = mt5.symbol_info_tick("EURGBP")
        return eurusd.ask, eurusd.bid, gbpusd.ask, gbpusd.bid,\
            eurgbp.ask, eurgbp.bid, ((1 / eurusd.bid) * gbpusd.ask * eurgbp.ask)

    def run_strategy(self):
        close, open1, open2, open3, open4, calc_time = self.open_close_levels()
        while True:
            if pd.Timestamp.now() - calc_time > pd.Timedelta(minutes=10):
                close, open1, open2, open3, open4, calc_time = self.open_close_levels()

            eurusd_pos, gbpusd_pos = self.get_positions()
            eu_ask, eu_bid, gu_ask, gu_bid, eg_ask, eg_bid, index_val = self.get_live_ticks()

            print(f'index val = {round(index_val, 5)}', f'open1={round(open1, 5)}',
                  f'open2={round(open2, 5)}', f'open3={round(open3, 5)}',
                  f'open4={round(open4, 5)}', f'close={round(close, 5)}')

            if index_val <= open1 and index_val > open2:
                if len(gbpusd_pos) < 5:
                    logging.info(f'GBPUSD BUY ORDER at {gu_ask} - index_val={index_val} - Open Level = {open1}')
                    res = buy_order(symbol='GBPUSD', lot=self.lot1, price=gu_ask,
                                    deviation=self.deviation, stop_loss=self.stop_loss)
                    logging.info(f'{res}')
                if len(eurusd_pos) < 5:
                    logging.info(f'EURUSD SELL ORDER at {eu_bid} - index_val={index_val} - Open Level = {open1}')
                    res = sell_order(symbol='EURUSD', lot=self.lot1, price=eu_bid,
                               deviation=self.deviation, stop_loss=self.stop_loss)
                    logging.info(f'{res}')
            elif index_val <= open2 and index_val > open3:
                if len(gbpusd_pos) < 5:
                    logging.info(f'GBPUSD BUY ORDER at {gu_ask} - index_val={index_val} - Open Level = {open2}')
                    res = buy_order(symbol='GBPUSD', lot=self.lot2, price=gu_ask,
                              deviation=self.deviation, stop_loss=self.stop_loss)
                    logging.info(f'{res}')
                if len(eurusd_pos) < 5:
                    logging.info(f'EURUSD SELL ORDER at {eu_bid} - index_val={index_val} - Open Level = {open2}')
                    res = sell_order(symbol='EURUSD', lot=self.lot2, price=eu_bid,
                               deviation=self.deviation, stop_loss=self.stop_loss)
                    logging.info(f'{res}')
            elif index_val <= open3 and index_val > open4:
                if len(gbpusd_pos) < 5:
                    logging.info(f'GBPUSD BUY ORDER at {gu_ask} - index_val={index_val} - Open Level = {open3}')
                    res = buy_order(symbol='GBPUSD', lot=self.lot3, price=gu_ask,
                              deviation=self.deviation, stop_loss=self.stop_loss)
                    logging.info(f'{res}')
                if len(eurusd_pos) < 5:
                    logging.info(f'EURUSD SELL ORDER at {eu_bid} - index_val={index_val} - Open Level = {open3}')
                    res = sell_order(symbol='EURUSD', lot=self.lot3, price=eu_bid,
                               deviation=self.deviation, stop_loss=self.stop_loss)
                    logging.info(f'{res}')
            elif index_val <= open4:
                if len(gbpusd_pos) < 5:
                    logging.info(f'GBPUSD BUY ORDER at {gu_ask} - index_val={index_val} - Open Level = {open4}')
                    res = buy_order(symbol='GBPUSD', lot=self.lot4, price=gu_ask,
                              deviation=self.deviation, stop_loss=self.stop_loss)
                    logging.info(f'{res}')
                if len(eurusd_pos) < 5:
                    logging.info(f'EURUSD SELL ORDER at {eu_bid} - index_val={index_val} - Open Level = {open4}')
                    res = sell_order(symbol='EURUSD', lot=self.lot4, price=eu_bid,
                               deviation=self.deviation, stop_loss=self.stop_loss)
                    logging.info(f'{res}')

            if index_val >= close:
                for pos in gbpusd_pos:
                    logging.info(f'GBPUSD CLOSE BUY ORDER as {gu_bid} - index_val={index_val} - Close Level = {close}')
                    res = close_buy_order(price=gu_bid, deviation=self.deviation, position=pos)
                    logging.info(f'{res}')
                for pos in eurusd_pos:
                    logging.info(f'EURUSD CLOSE SELL ORDER as {eu_ask} - index_val={index_val} - Close Level = {close}')
                    res = close_sell_order(price=eu_ask, deviation=self.deviation, position=pos)
                    logging.info(f'{res}')


if __name__ == '__main__':
    mt5_connect_and_auth(strategy='demo_triarb_v1')
    triarb = TriangleArb(lot=0.01, deviation=[0, 0], stop_loss=0.002)
    triarb.run_strategy()