from logging_functions.class_logging import Logger
import pandas as pd
from datetime import datetime
import MetaTrader5 as mt5
import pytz
from src.project_helper_functions.helpers import convert_to_utc

class HistoricalDataExtractor:
    def __init__(self, symbol: str):
        self.logger = Logger(f"{symbol}_historical_extractor").logger
        self.symbol = symbol

    def get_rates_data(self, start: str, end: str, freq):
        start = convert_to_utc(start)
        end = convert_to_utc(end)
        data = mt5.copy_rates_range(self.symbol, mt5.TIMEFRAME_M1, start, end)
        if data is None:
            print(mt5.last_error())
        else:
            data = pd.DataFrame(data)
            data['time'] = pd.to_datetime(data['time'], unit='s')
            self.data = data



    def get_ticks_range(self, start: str, end: str):
        ticks = mt5.copy_ticks_range(self.symbol, convert_to_utc(start), convert_to_utc(end), mt5.COPY_TICKS_ALL)
        # create DataFrame out of the obtained data
        ticks_frame = pd.DataFrame(ticks)
        # convert time in seconds into the datetime format
        ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
        ticks_frame = ticks_frame[['time', 'bid', 'ask']]
        for col in ticks_frame.columns:
            if col != 'time':
                ticks_frame = ticks_frame.rename(columns={col: f'{self.symbol.lower()}_{col}'})
        return ticks_frame