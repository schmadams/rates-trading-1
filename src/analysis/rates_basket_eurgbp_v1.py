from src.extractors.historical_extractor import HistoricalDataExtractor
from src.project_helper_functions.mt5_engine import MetaTraderConnection
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
class RatesBasketEURGBPV1(MetaTraderConnection):
    data = {}
    def __init__(self, timeframe, start, end):
        super().__init__()
        self.timeframe = timeframe
        self.start, self.end = start, end
        self.run_extractors()
        self.ratio_analysis()

    def run_extractors(self):
        eurusd_class = HistoricalDataExtractor(symbol='EURUSD')
        eurusd_class.get_rates_data(start=self.start, end=self.end, freq=self.timeframe)
        self.data.update(
            {
                'eurusd': eurusd_class.data
            }
        )

        gbpusd_class = HistoricalDataExtractor(symbol='GBPUSD')
        gbpusd_class.get_rates_data(start=self.start, end=self.end, freq=self.timeframe)
        self.data.update(
            {
                'gbpusd': gbpusd_class.data
            }
        )

        uj_class = HistoricalDataExtractor(symbol='USDJPY')
        uj_class.get_rates_data(start=self.start, end=self.end, freq=self.timeframe)
        self.data.update(
            {
                'usdjpy': uj_class.data
            }
        )

    def ratio_analysis(self):
        gu_df = self.data['gbpusd'].rename(columns={'close': 'gu_close'}).copy()
        eu_df = self.data['eurusd'].rename(columns={'close': 'eu_close'}).copy()
        uj_df = self.data['usdjpy'].rename(columns={'close': 'uj_close'}).copy()
        uj_df = uj_df[['time', 'uj_close']]
        gu_df = gu_df[['time', 'gu_close']]
        eu_df = eu_df[['time', 'eu_close']]
        merged = gu_df.merge(eu_df, how='left', on='time')
        merged = merged.merge(uj_df, how='left', on='time')
        merged['ratio'] = merged['eu_close'] * merged['gu_close'] * merged['uj_close']
        plt.plot(merged['time'], merged['ratio'])
        plt.show()
        a=1
        a=1





if __name__ == '__main__':
    RatesBasketEURGBPV1(timeframe=mt5.TIMEFRAME_H1, start='01-12-2023 12:30:45', end='01-02-2024 12:30:45')



