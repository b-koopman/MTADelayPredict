"""
Utility functions for plotting train traffic around alerts
"""
import sys
import os
import pandas as pd

from MTADelayPredict.utils import gtfs_loader
from MTADelayPredict.subway_line import SubwayLine, N_STOP_LIST
from MTADelayPredict.stop import Stop
from MTADelayPredict.plotting import traffic

def load_range_schedule(start_date, end_date,
                        stop_filter, route_filter,
                        data_dir,
                        train_line = 'nqrw'):

    loader = gtfs_loader.GTFSLoader(data_dir=data_dir,
                                    train_line='nqrw')
    loader.load_range(start_date, end_date, stop_filter=stop_filter, route_filter=route_filter, verbose=True, schedule=True)

    schedule_dfs = []
    for stop, train in zip(loader.stop_dict.items(), loader.train_dict.items()):
        schedule_dfs.append(pd.DataFrame(stop[1], index=train[1], columns=[stop[0]]))

    # Change to numerical index for stops so plotting is a little easier
    line = SubwayLine(N_STOP_LIST)
    schedule_df = pd.concat(schedule_dfs)
    schedule_df.sort_index(inplace=True)
    schedule_df = schedule_df[start_date:end_date]
    schedule_df = schedule_df.applymap(lambda x: line.stop_idx(x) if not isinstance(x, float) else x)
    schedule_df.reset_index(inplace=True)
    schedule_df.reset_index(inplace=True)
    return schedule_df

def plot_alert(alert_time, observing_stop, alert_stop,
               stop_filter, route_filter,
               title='Northbound N Trains',
               data_dir = '../data/raw/status'
               ):
    """
    Create a windowed plot of train traffic around a certain train alert time

    :param alert_time: Time alert was seen
    :param observing_stop: Stop we're looking for effects at, annotate this stop for comparison (green)
    :param alert_stop: Stop alert occured at, annotate stop for comparison (red)
    :return: figure of plot
    """
    import matplotlib.lines as mlines
    import matplotlib.pyplot as plt

    start_time = alert_time - pd.Timedelta(15, unit='m')
    end_time = alert_time + pd.Timedelta(60, unit='m')

    # Fetch schedule data and plot
    schedule_df = load_range_schedule(start_time, end_time, stop_filter, route_filter, data_dir)
    ax = traffic.plot_traffic(start_time, end_time, schedule_df)

    current_line = SubwayLine(N_STOP_LIST)
    # Annotate observing stop
    xmin, xmax = ax.get_xbound()
    ymin = ymax = current_line.stop_idx(observing_stop)
    stop_line = mlines.Line2D([xmin, xmax], [ymin, ymax], color='g')
    ax.add_line(stop_line)

    ymin = ymax = current_line.stop_idx(alert_stop)
    alert_line = mlines.Line2D([xmin, xmax], [ymin, ymax], color='r')
    ax.add_line(alert_line)

    xmin = xmax = alert_time
    ymin, ymax = ax.get_ybound()
    pd.DataFrame([[ymin], [ymax]], index=[xmin, xmax]).plot(color='r', ax=ax)
    ax.legend((stop_line, alert_line), ('observing stop', 'alert'))
    ax.set_xlabel('Time')
    ax.set_ylabel('Stop')
    ax.set_title("{} @ {}".format(title, alert_time))
    return plt.gcf()