"""
Helpers for loading in train data for use in building features
"""

from MTADelayPredict.data_processing import gtfs_loader
from MTADelayPredict.subway_line import SubwayLine, N_STOP_LIST
import pandas as pd
import numpy as np

def min_until_train(loader):
    """
    Calculate the cumulative minutes until the next train arrives

    :param loader: loaded GTFSLoader to extract data from
    :return: DataFrame of [time x stop_id] with value of minutes
    """
    import re

    schedule_dfs = []
    for stop, train in zip(loader.stop_dict.items(), loader.time_dict.items()):
        schedule_dfs.append(pd.DataFrame(stop[1], index=train[1], columns=[stop[0]]))
    line = SubwayLine(N_STOP_LIST)
    df = pd.concat(schedule_dfs)
    df.columns = df.columns.map(lambda x: float(re.sub(r'[^0-9]+', '', x)) if isinstance(x, str) else x)
    # TODO: Turn this into a data check
    df = df.sort_index()['2000-01-01':]

    df = df.stack().reset_index()
    df.columns = ['time', 'train_id', 'stop_id']
    df = df.pivot_table(index='time', columns='stop_id', values='train_id', aggfunc=np.max)
    df.sort_index(inplace=True)
    df = df.resample('1T').last()

    train_gaps = df.copy().shift(1)
    train_gaps[~df.isna()] = 0.0
    train_gaps.fillna(method='ffill', inplace=True)
    train_gaps.replace(0.0, np.nan, inplace=True)
    min_since_train_df = train_gaps.copy()

    min_since_train_df[~train_gaps.isna()] = 1.0
    min_since_train_df = min_since_train_df.astype(float)

    min_until_train_df = min_since_train_df.iloc[::-1].copy()
    reversed_train_gaps = train_gaps.iloc[::-1]
    reversed_train_gaps = reversed_train_gaps.reset_index(drop=True)
    min_until_train_df = min_until_train_df.reset_index(drop=True)

    for observing_stop in df.columns:
        min_until_train_df[observing_stop] = min_until_train_df[observing_stop].groupby(
            reversed_train_gaps[observing_stop]).cumsum()

    min_until_train_df = min_until_train_df.iloc[::-1]
    min_until_train_df.index = min_since_train_df.index

    return min_until_train_df

def min_since_train(loader):
    """
    Calculate the cumulative minutes since the last train seen at a given station

    :param loader: loaded GTFSLoader to extract data from
    :return: DataFrame of [time x stop_id] with valus of minutes
    """
    import re

    schedule_dfs = []
    for stop, train in zip(loader.stop_dict.items(), loader.time_dict.items()):
        schedule_dfs.append(pd.DataFrame(stop[1], index=train[1], columns=[stop[0]]))
    line = SubwayLine(N_STOP_LIST)
    df = pd.concat(schedule_dfs)
    df.columns = df.columns.map(lambda x: float(re.sub(r'[^0-9]+', '', x)) if isinstance(x, str) else x)
    # TODO: Turn this into a data check
    df = df.sort_index()['2000-01-01':]

    df = df.stack().reset_index()
    df.columns = ['time', 'train_id', 'stop_id']
    df = df.pivot_table(index='time', columns='stop_id', values='train_id', aggfunc=np.max)
    df.sort_index(inplace=True)
    df = df.resample('1T').last()

    train_gaps = df.copy().shift(1)
    train_gaps[~df.isna()] = 0.0
    train_gaps.fillna(method='ffill', inplace=True)
    train_gaps.replace(0.0, np.nan, inplace=True)
    min_since_train_df = train_gaps.copy()

    min_since_train_df[~train_gaps.isna()] = 1.0
    min_since_train_df = min_since_train_df.astype(float)

    for observing_stop in df.columns:
        min_since_train_df[observing_stop] = min_since_train_df[observing_stop].groupby(
            train_gaps[observing_stop]).cumsum()

    return min_since_train_df


def min_in_station(loader):
    """
    Calculate the cumulative minutes a train has been in a station
    :param loader: GTFSLoader to load data from
    :return: DataFrame of [ time x stop_id ], data is in units of minutes
    """
    import re
    schedule_dfs = []
    for stop, train in zip(loader.stop_dict.items(), loader.time_dict.items()):
        schedule_dfs.append(pd.DataFrame(stop[1], index=train[1], columns=[stop[0]]))
    line = SubwayLine(N_STOP_LIST)
    df = pd.concat(schedule_dfs)
    df.columns = df.columns.map(lambda x: float(re.sub(r'[^0-9]+', '', x)) if isinstance(x, str) else x)
    df = df.sort_index()['2000-01-01':]

    df = df.stack().reset_index()
    df.columns = ['time', 'train_id', 'stop_id']
    df = df.pivot_table(index='time', columns='stop_id', values='train_id', aggfunc=np.max)
    df.sort_index(inplace=True)
    df = df.resample('1T').last()

    min_in_station_df = df.copy()
    min_in_station_df[~df.isna()] = 1.0
    min_in_station_df = min_in_station_df.astype(float)

    for observing_stop in df.columns:
        min_in_station_df[observing_stop] = min_in_station_df[observing_stop].groupby(df[observing_stop]).cumsum()

    return min_in_station_df


def load_range_schedule(loader):
    """
    Load in data from a GTFSLoader that can be used to generate a "schedule" of every train's path
    NOTE: This should only be used on daily grouped data , otherwise there will be
    train naming conflicts

    The resulting dataframe is [time x train_id] containing the current stop_id of the train

    :param loader: A loaded loader object
    :return: a data frame that is dimensioned [time x train_id]
    """

    if len(loader.stop_dict) == 0:
        raise ValueError("loader has no data, loaded.  Call GTFSLoader.load_range(...) first")

    schedule_dfs = []
    for stop, train in zip(loader.stop_dict.items(), loader.time_dict.items()):
        schedule_dfs.append(pd.DataFrame(stop[1], index=train[1], columns=[stop[0]]))

    # Change to numerical index for stops so plotting is a little easier
    line = SubwayLine(N_STOP_LIST)
    schedule_df = pd.concat(schedule_dfs)
    schedule_df.sort_index(inplace=True)
    # Remove 0 UNIX time values, safeguard to avoid exploding memory if 0 accidentally passed
    schedule_df = schedule_df['2000-01-01':]
    schedule_df = schedule_df.applymap(lambda x: line.stop_idx(x) if not isinstance(x, float) else x)
#    schedule_df.drop_duplicates(keep='last', inplace=True)
    schedule_df.reset_index(inplace=True)
    schedule_df.reset_index(inplace=True)

    return schedule_df
