import warnings

# Ignore deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import pandas as pd
import MetaTrader5 as mt5
from datetime import timedelta, datetime
from src.project_helper_functions.mt5_engine import mt5_connect_and_auth
from src.extractors.historical_extractor import HistoricalDataExtractor
import matplotlib.pyplot as plt
import numpy as np

def create_sequences(data, input_steps=20, forecast_steps=10):
    X, y = [], []
    for i in range(len(data) - input_steps - forecast_steps + 1):
        print(i, len(data) - input_steps - forecast_steps + 1)
        X.append(data.iloc[i:(i + input_steps)][['K', 'D']].values)
        y.append(data.iloc[(i + input_steps):(i + input_steps + forecast_steps)][['K', 'D']].values)
    return np.array(X), np.array(y)

 # Assuming this is your DataFrame with 'K' and 'D' columns



def calculate_stochastic_oscillator(df, n=14, d=3):
    """
    Calculates the Stochastic Oscillator for the given DataFrame.
    Args:
    - df: DataFrame with the columns 'high', 'low', and 'close'.
    - n: Period for %K calculation.
    - d: Period for %D calculation (SMA of %K).

    Adds the %K and %D columns to the DataFrame.
    """
    # Calculate %K
    low_min = df['low'].rolling(window=n, min_periods=1).min()
    high_max = df['high'].rolling(window=n, min_periods=1).max()
    df['K'] = ((df['close'] - low_min) / (high_max - low_min)) * 100
    df['D'] = df['K'].rolling(window=d, min_periods=1).mean()
    # plotdf = df[:500]
    # plt.plot(plotdf['K'])
    # plt.plot(plotdf['D'])
    # plt.show()
    df = df[['time', 'close', 'K', 'D']]
    return df


def get_data(start, end, symbol):
    dtrng = pd.date_range(start=start, end=end, freq='D')
    data = [] b#g]tr=rd-x8765t     r    edsaz
        day_df = pd.DataFrame(mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, day, day + timedelta(days=1)))
        data.append(day_df)
    data = pd.concat(data)
    data['time'] = pd.to_datetime(data['time'], unit='s')
    data = data.drop_duplicates(subset='time')
    # Ensure the DataFrame is sorted by time
    data.sort_values('time', inplace=True)
    return data


def run(start, end, symbol, strategy):
    mt5_connect_and_auth(strategy=strategy)
    data = get_data(start, end, symbol)
    data = calculate_stochastic_oscillator(data)
    #

    X, y = create_sequences(data)
    # Now `data` contains the stochastic oscillator columns '%K' and '%D'
    return data


if __name__ == '__main__':
    start = datetime(year=2024, month=2, day=10)
    end = datetime(year=2024, month=2, day=27)
    data = run(symbol='EURUSD', start=start, end=end, strategy='demo_bnn_stoch_search_10k')
    # Optionally, save or print your data
    print(data.head())
,llop[''
|]