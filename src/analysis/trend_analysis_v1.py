import warnings

# Ignore deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import MetaTrader5 as mt5
import pandas as pd
from src.project_helper_functions.mt5_engine import mt5_connect_and_auth
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

mt5_connect_and_auth(strategy='demo_triarb_v1')

def engineer_data(symbol, start, end):
    df = get_ticks(symbol, start, end)
    df = RSI_calc(df, n=2000)
    RSI_analysis(symbol, df)
    a=1
    a=1

def RSI_analysis(symbol, df):
    df['delta'] = df['bid'].shift(-100) - df['ask']
    df['buy'] = [1 if x < 25 else 0 for x in df['RSI']]
    df = df[:50000]
    # Create figure and axis
    fig, ax1 = plt.subplots()

    # Plot the first column (RSI) on the first y-axis
    color = 'tab:red'
    ax1.set_xlabel('Index')  # Assuming the x-axis is the DataFrame index
    ax1.set_ylabel('RSI', color=color)
    ax1.plot(df.index, df['RSI'],
             color=color)  # If you have a specific column for x-axis, replace df.index with df['your_column']
    ax1.tick_params(axis='y', labelcolor=color)

    # Create a second y-axis for the second column (ask)
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('ask', color=color)
    ax2.plot(df.index, df['ask'], color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    # Show the plot
    plt.show()

    a=1
    a=1


def RSI_calc(ticks_df, n=300):
    ticks_df['mid_price'] = (ticks_df['bid'] + ticks_df['ask']) / 2

    # Calculate price changes (delta)
    ticks_df['delta'] = ticks_df['mid_price'].diff()

    # Identify gains and losses
    ticks_df['gain'] = np.where(ticks_df['delta'] > 0, ticks_df['delta'], 0)
    ticks_df['loss'] = np.where(ticks_df['delta'] < 0, abs(ticks_df['delta']), 0)
    ticks_df['avg_gain'] = ticks_df['gain'].rolling(window=n, min_periods=n).mean()
    ticks_df['avg_loss'] = ticks_df['loss'].rolling(window=n, min_periods=n).mean()

    # Use exponential smoothing formula to calculate subsequent average gains and losses
    ticks_df['avg_gain'] = ticks_df['avg_gain'].fillna(method='bfill')  # Backfill the initial NaNs
    ticks_df['avg_loss'] = ticks_df['avg_loss'].fillna(method='bfill')

    # The initial values are correctly set by rolling mean, now apply smoothing
    ticks_df['avg_gain'] = ticks_df['avg_gain'].ewm(alpha=1 / n, adjust=False).mean()
    ticks_df['avg_loss'] = ticks_df['avg_loss'].ewm(alpha=1 / n, adjust=False).mean()

    # Calculate RS and RSI
    ticks_df['RS'] = ticks_df['avg_gain'] / ticks_df['avg_loss']
    ticks_df['RSI'] = 100 - (100 / (1 + ticks_df['RS']))
    return ticks_df[['time', 'ask', 'bid', 'RSI']]

def get_rates_day(symbol, start, end, timeframe):
    df = mt5.copy_rates_range(symbol, timeframe, start, end)
    df = pd.DataFrame(df)
    df.to_pickle(f'../data/RATES_{symbol}_{str(start.strftime("%Y%m%d"))}_{str(end.strftime("%Y%m%d"))}_{timeframe}.pkl')
    a=1
    a=1

def get_ticks(symbol, start, end):
    all_ticks = []
    for day in pd.date_range(start, end, freq='D'):
        ticks = pd.DataFrame(mt5.copy_ticks_range(symbol, day, day + timedelta(days=1), mt5.COPY_TICKS_ALL))
        all_ticks.append(ticks)
    all_ticks = pd.concat(all_ticks)
    all_ticks = all_ticks[['time_msc', 'ask', 'bid']].rename(columns={'time_msc': 'time'})
    all_ticks['time'] = pd.to_datetime(all_ticks['time'], unit='ms')
    all_ticks = all_ticks.sort_values(by='time').reset_index()
    # all_ticks.to_pickle(f'../data/TICKS_{symbol}_{str(start.strftime("%Y%m%d"))}_{str(end.strftime("%Y%m%d"))}_{timeframe}.pkl')
    return all_ticks



if __name__ == '__main__':
    symbol = 'EURUSD'
    start = datetime(year=2024, month=3, day=1)
    end = datetime(year=2024, month=3, day=6)
    # timeframe = mt5.TIMEFRAME_M1
    engineer_data(symbol, start, end)
