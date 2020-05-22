import pandas as pd

from MTADelayPredict.data_processing import gtfs_loader
from MTADelayPredict.subway_line import SubwayLine, N_STOP_LIST


def load_range_schedule(start_date, end_date,
                        stop_filter, route_filter,
                        data_dir,
                        train_line = 'nqrw'):

    loader = gtfs_loader.GTFSLoader(data_dir=data_dir,
                                    train_line='nqrw')
    data = loader.load_range(start_date, end_date, stop_filter=stop_filter, route_filter=route_filter, verbose=True, schedule=True)

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

    data['schedule_df'] = schedule_df
    data['loader'] = loader
    return data