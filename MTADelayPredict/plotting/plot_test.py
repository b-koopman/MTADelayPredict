# relative MTADelayPredict Project
import sys
import os
import pandas as pd

from MTADelayPredict.utils import gtfs_loader
from MTADelayPredict.plotting import alerts

alert_time = pd.Timestamp('2018-08-07 16:51:00', tz='US/Eastern')
STOP_FILTER = '^.*N$'
ROUTE_FILTER = 'N'
alerts.plot_alert(alert_time, observing_stop='R16N', alert_stop='R11N',\
                  stop_filter=STOP_FILTER, route_filter=ROUTE_FILTER,
                  data_dir='/media/Data1/Udacity/MLEngineer/MTADelayPredict/data/raw/status')