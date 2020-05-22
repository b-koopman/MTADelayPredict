import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(os.path.join('DataExploration.ipynb')))))
from MTADelayPredict.utils import  stop_info
from MTADelayPredict.subway_line import SubwayLine, N_STOP_LIST
from MTADelayPredict.stop import Stop
from importlib import reload
from MTADelayPredict.data_processing import train_data, gtfs_loader
from MTADelayPredict.features import feature_builder

class testFeatureBuilder:
    @classmethod
    def setup_class(cls):
        STOP_FILTER = '^.*N$'
        ROUTE_FILTER = 'N'
        data_dir = '../data/raw/status'

        start_date = pd.Timestamp('2018-08-01 11:26:00-04:00', tz='US/Eastern')
        end_date = pd.Timestamp('2018-08-01 15:26:00-04:00', tz='US/Eastern')
        train_line = 'nqrw'
        cls.loader = gtfs_loader.GTFSLoader(data_dir=data_dir,
                                        train_line=train_line)
        cls.loader.load_range(start_date, end_date, stop_filter=STOP_FILTER, route_filter=ROUTE_FILTER, verbose=True,
                          schedule=True)

        cls.min_since_train = train_data.min_since_train(cls.loader)
        cls.min_in_station = train_data.min_in_station(cls.loader)


    @classmethod
    def teardown_class(cls):
        del cls.loader

    def test_build_features(self):
        features = feature_builder.FeatureBuilder(self.min_in_station,
                                                  self.min_since_train)

        # TODO: Test for dimensionality, required features etc...
        assert not features.features.empty
