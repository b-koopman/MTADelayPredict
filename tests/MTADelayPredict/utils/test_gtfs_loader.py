from nose.tools import assert_equal

from MTADelayPredict.data_processing import gtfs_loader


def testDatetime():
    """
    Test simple datetime conversion util to get datetime out of a gtfs filename
    """
    import pandas as pd
    filename = 'gtfs_nqrw_20181209_064712.gtfs'
    assert_equal(gtfs_loader.gtfs_datetime(filename), \
                 pd.Timestamp('2018-12-09 06:47:12').tz_localize('US/Eastern'))

    filename = 'gtfs_j_20181209_064712.gtfs'
    assert_equal(gtfs_loader.gtfs_datetime(filename), \
                 pd.Timestamp('2018-12-09 06:47:12').tz_localize('US/Eastern'))


def testFiles():
    """
    Test that files are loaded appropriately across dates
    """
    import pandas as pd
    import os

    test_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(os.path.join('test_gtfs_loader.py')))))
    loader = gtfs_loader.GTFSLoader(data_dir=os.path.join(test_dir + '/data/gtfs'),
                                    train_line='nqrw')

    # Make sure that the correct number of files have been loaded for a single day
    # The test data has one file per hour
    file_list = loader.list_files(start_date=pd.Timestamp('2019-01-01 00:00:00').tz_localize('US/Eastern'),
                                  end_date=pd.Timestamp('2019-01-01 23:59:59').tz_localize('US/Eastern'))
    assert_equal(len(file_list), 24)

    # Load across days
    file_list = loader.list_files(start_date=pd.Timestamp('2019-01-01 00:00:00').tz_localize('US/Eastern'),
                                  end_date=pd.Timestamp('2019-01-02 23:59:59').tz_localize('US/Eastern'))
    assert_equal(len(file_list), 48)
    assert_equal(gtfs_loader.gtfs_datetime(os.path.basename(file_list[-1])), \
                 pd.Timestamp('2019-01-02 23:01:00').tz_localize('US/Eastern'))

    # Load across months
    file_list = loader.list_files(start_date=pd.Timestamp('2019-01-01 00:00:00').tz_localize('US/Eastern'),
                                  end_date=pd.Timestamp('2019-02-04 23:59:59').tz_localize('US/Eastern'))
    assert_equal(len(file_list), 3 * 2 * 24)
    assert_equal(gtfs_loader.gtfs_datetime(os.path.basename(file_list[-1])), \
                 pd.Timestamp('2019-02-03 23:01:00').tz_localize('US/Eastern'))

    file_times = set(map(gtfs_loader.gtfs_datetime, map(os.path.basename, file_list)))
    expected_times = set([pd.Timestamp('2019-01-01 23:01:00').tz_localize('US/Eastern'), \
                          pd.Timestamp('2019-01-02 23:01:00').tz_localize('US/Eastern'), \
                          pd.Timestamp('2019-01-03 23:01:00').tz_localize('US/Eastern'), \
                          pd.Timestamp('2019-02-03 23:01:00').tz_localize('US/Eastern')])
    assert (expected_times.issubset(file_times))
