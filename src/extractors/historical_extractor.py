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



