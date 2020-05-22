# relative MTADelayPredict Project
import sys
import os
import pandas as pd
import numpy as np

from MTADelayPredict.utils import  stop_info
from MTADelayPredict.subway_line import SubwayLine, N_STOP_LIST
from MTADelayPredict.stop import Stop
from importlib import reload
from MTADelayPredict.data_processing import train_data, gtfs_loader

class testTrainData():
    @classmethod
    def setup_class(cls):
        STOP_FILTER = '^.*N$'
        ROUTE_FILTER = 'N'
        data_dir = '../data/raw/status'

        A = set(['A', 'B'])
        B = set(['A'])

        A.intersection(B)

        start_date = pd.Timestamp('2018-08-01 11:26:00-04:00', tz='US/Eastern')
        end_date = pd.Timestamp('2018-08-01 15:26:00-04:00', tz='US/Eastern')
        train_line = 'nqrw'
        cls.loader = gtfs_loader.GTFSLoader(data_dir=data_dir,
                                        train_line=train_line)
        cls.loader.load_range(start_date, end_date, stop_filter=STOP_FILTER, route_filter=ROUTE_FILTER, verbose=True,
                          schedule=True)

    @classmethod
    def teardown_class(cls):
        del cls.loader

    def test_min_since_train(self):
        """
        Quick test load for minutes since a train
        """

        min_since_train = train_data.min_since_train(self.loader)
        assert not min_since_train.empty

    def test_min_in_station(self):
        """
        Quick test load for minutes a train has been in the station
        """

        min_in_station = train_data.min_in_station(self.loader)
        assert not min_in_station.empty

    def test_load_range_schedule(self):
        schedule_df = train_data.load_range_schedule(self.loader)
        assert not schedule_df.empty