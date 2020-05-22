import sys
import os
import pandas as pd
import numpy as np

import MTADelayPredict.plotting.train_data

# relative MTADelayPredict Project
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(os.path.join('DataExploration.ipynb')))))
from MTADelayPredict.data_processing import train_data, gtfs_loader


def test_scheduled_arrival():
    STOP_FILTER = '^.*N$'
    ROUTE_FILTER = 'N'
    data_dir = '../data/raw/status'

    start_date = pd.Timestamp('2018-08-01 11:26:00-04:00', tz='US/Eastern')
    end_date = pd.Timestamp('2018-08-01 15:26:00-04:00', tz='US/Eastern')
    train_line = 'nqrw'
    loader = gtfs_loader.GTFSLoader(data_dir=data_dir,
                                    train_line=train_line)
    data = loader.load_range(start_date, end_date, stop_filter=STOP_FILTER, route_filter=ROUTE_FILTER, verbose=True,
                             schedule=True)

    assert data == None

    assert not loader.next_scheduled_arrival_df.empty
