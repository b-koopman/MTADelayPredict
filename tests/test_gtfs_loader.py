from MTADelayPredict.utils import gtfs_loader

import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(os.path.join('DataExploration.ipynb')))))
from MTADelayPredict.utils import gtfs_loader, stop_info
from MTADelayPredict.subway_line import SubwayLine, N_STOP_LIST
from MTADelayPredict.stop import Stop
from importlib import reload
from MTADelayPredict.plotting import alerts

def test_basic_load():
    STOP_FILTER = '^.*N$'
    ROUTE_FILTER = 'N'
    data_dir = '../data/raw/status'

    start_date = pd.Timestamp('2018-08-01 11:26:00-04:00', tz='US/Eastern')
    end_date = pd.Timestamp('2018-08-01 15:26:00-04:00', tz='US/Eastern')
    data = alerts.load_range_schedule(start_date, \
                                      end_date, \
                                      STOP_FILTER, ROUTE_FILTER, data_dir)

    next_scheduled_df = data['next_scheduled_arrival']
    assert not next_scheduled_df.replace(0.0, np.nan).dropna(how='all').empty

    schedule_df = data['schedule_df']
    assert not schedule_df.replace(0.0, np.nan).dropna(how='all').empty

