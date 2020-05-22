"""
Utility functions for plotting train traffic around alerts
"""
import pandas as pd

from MTADelayPredict.data_processing import train_data
from MTADelayPredict.subway_line import SubwayLine, N_STOP_LIST
from MTADelayPredict.plotting import traffic


def plot_alert(alert_time, observing_stop, alert_stop,
               stop_filter, route_filter,
               title='Northbound N Trains',
               data_dir = '../data/raw/status',
               start_window = 15,
               end_window = 60,
               ):
    """
    Create a windowed plot of train traffic around a certain train alert time, using matplotlib

    :param alert_time: Time alert was seen
    :param observing_stop: Stop we're looking for effects at, annotate this stop for comparison (green)
    :param alert_stop: Stop alert occured at, annotate stop for comparison (red)
    :return: figure of plot
    """
    import matplotlib.lines as mlines
    import matplotlib.pyplot as plt

    start_time = alert_time - pd.Timedelta(start_window, unit='m')
    end_time = alert_time + pd.Timedelta(end_window, unit='m')

    # Fetch schedule data and plot
    schedule_df = train_data.load_range_schedule(start_time, end_time, stop_filter, route_filter, data_dir)
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