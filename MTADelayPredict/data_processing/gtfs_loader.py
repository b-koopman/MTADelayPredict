from MTADelayPredict.utils.utils import grouper, gtfs_datetime
from MTADelayPredict.data_processing.merged_entity import MergedEntity
import pandas as pd

# Load in the protobuf APIs
try:
    import MTADelayPredict.protobuf.nyct_subway_pb2 as nyct_subway_pb2
except ImportError:
    raise ImportError('nyct_subway_pb2 not found, make sure protobuf is compiled, see DataExploration.ipynb')
try:
    import MTADelayPredict.protobuf.gtfs_realtime_pb2 as gtfs_realtime_pb2
except ImportError:
    raise ImportError('gtfs_realtime_pb2 not found, make sure protobuf is compiled, see DataExploration.ipynb')
    
# There is a problem where the vehicle entites don't provide an easily discernable stop name, just an ID
# However, the entities are paired up in as trip_entity  and vehicle entity
# We can just iterate through the entities in groups of 2, and we always know what stop we are actually stopped at

# TODO: Examine cases where this isn't well broken up into trip_update/vehicle pairings, maybe there are some other fun messages there
def get_entities(msg, verbose=False):
    for trip_entity,vehicle_entity in grouper(msg.entity, 2):
        
        try:
            assert trip_entity.HasField('trip_update')
            assert vehicle_entity.HasField('vehicle')
            assert trip_entity.trip_update.trip.trip_id == vehicle_entity.vehicle.trip.trip_id
        except Exception as e:
            if verbose:
                print("Skipping entity pairing @ {}".format(pd.to_datetime(msg.header.timestamp, unit='s', utc=True).tz_convert('US/Eastern')))
            continue 
            
        yield(MergedEntity(trip_entity, vehicle_entity))
        
def build_stop_id_index(data_dir, stop_filter='*'):
    try:
        stop_ids = pd.read_csv(data_dir+'/google_transit/stops.txt')
        return pd.Index(stop_ids[stop_ids['stop_id'].str.match(stop_filter)]['stop_id'], name='stop_id')
    except:
        raise Exception("stops.txt not found, Requires MTA Google transit files downloaded and extracted from http://web.mta.info/developers/data/nyct/subway/google_transit.zip to <data_dir>/google_transit")
        


class GTFSLoader: 
    """
    Class to iterate through gtfs files across a date range for a given train_line, loading and parsing
    """
    def __init__(self, data_dir, train_line):
        """
        data_dir: Toplevel directory containing the date directory tree of gtfs files
        data_dir is expected to be a directory formatted like so:
        201901/
            20190101/
                
        201902/
        ...
        
        train_line: specify which train line to use, such as nqrw, j etc...
        e.g. gtfs_nqrw_20181209_064712.gtfs would have "nqrw" as the train_line
        """
        from collections import defaultdict
        import os

        if not os.path.isdir(data_dir):
            raise ValueError("data_dir {} does not exist, cannot load gtfs files".format(data_dir))

        self.data_dir = data_dir
        self.train_line = train_line

        self.stopped_at_df = pd.DataFrame()
        self.next_train_df = pd.DataFrame()
        self.next_scheduled_arrival_df = pd.DataFrame()
        
    def list_files(self, start_date, end_date):
        """
        Helper to enumerate all file paths for a date range
        """
        import glob
        import os
        
        drange = pd.date_range(start_date, end_date, freq='D')
        
        file_list = []
        
        for date in drange:
            yyyymm = str(date.year * 100 + date.month)
            yyyymmdd = str(date.year * 10000 + date.month * 100 + date.day)
            filename = 'gtfs_{}_{}_*.gtfs'.format(self.train_line, yyyymmdd)
            gtfs_dir = os.path.join(self.data_dir, yyyymm, yyyymmdd)
            daily_files = glob.glob( os.path.join(gtfs_dir,filename))
            daily_files = [f for f in daily_files if (start_date <= gtfs_datetime(os.path.basename(f)) <= end_date)]
#            if len(daily_files) == 0:
#                print("WARNING: no files found for {} in {}".format(yyyymmdd, os.path.join(self.data_dir, yyyymm, yyyymmdd, filename)))
            file_list += daily_files
        
        return file_list

    def load_range(self, start_date, end_date, stop_filter='.*', route_filter='.*', verbose=False, schedule=False):
        """
        Load files for a given date range and return the resulting dataframe.
        This new data replaces any existing loaded data.
        
        If verbose, it will display a progress bar
        """
        import re
        import os
        import google.protobuf.message as message
        import numpy as np
        from collections import defaultdict
        from collections import OrderedDict

        from MTADelayPredict.subway_line import N_STOP_LIST

        start_min = (start_date - pd.Timestamp("1970-01-01").tz_localize('UTC').astimezone('US/Eastern')) // pd.Timedelta('1s') // 60
        end_min = (end_date - pd.Timestamp("1970-01-01").tz_localize('UTC').astimezone('US/Eastern')) // pd.Timedelta('1s') // 60
        # Add a few minutes, since sometimes we get updates from the futures
        print(end_min)
        end_min += 120
        print(end_min)
        stop_id_index = N_STOP_LIST
        new_stop_ids = set()
        stop_id_dict = {s:i for i,s in enumerate(stop_id_index)}
        stopped_at_np = np.zeros((end_min-start_min, len(stop_id_index)))
        stopped_at_np[:] = np.nan
        next_train_np = np.zeros((end_min-start_min, len(stop_id_index)))
        next_train_np[:] = np.nan

        # Keep track of when every train thinks it is going to arrive at each station
        def new_scheduled_arrival():
            next_scheduled_arrival_np = np.zeros((end_min-start_min, len(stop_id_index)))
            next_scheduled_arrival_np[:] = np.nan
            return next_scheduled_arrival_np
        train_schedule_np_dict = defaultdict(new_scheduled_arrival)
        
        if schedule:
            self.stop_dict =  defaultdict(list)
            self.time_dict =  defaultdict(list)


        if verbose:
            import progressbar
        
        # Get list of files
        gtfs_files = self.list_files(start_date, end_date)
        gtfs_files.sort()
        
        if verbose:
            widgets = [progressbar.Percentage(), progressbar.Bar(), progressbar.Variable('entries'), progressbar.Variable('decode_errors')]
            bar = progressbar.ProgressBar(widgets=widgets, max_value=len(gtfs_files), min_poll_interval=.4).start()
        fails = 0

        msg = gtfs_realtime_pb2.FeedMessage()

        for i,file in enumerate(gtfs_files):
            try:
                with open(os.path.join(file),'rb') as fh:
                    msg.ParseFromString(fh.read())
            except message.DecodeError as e:
                # Sometimes there are decode errors, OK if we miss a few, just keep an eye on it
                fails+=1
                continue

            if verbose:
                bar.update(i+1, entries=self.stopped_at_df.shape[0], decode_errors=fails)

            for merged_entity in get_entities(msg):
                # Ignore late night wrapround into the next day
                if merged_entity.time_raw >= end_min or merged_entity.time_raw < 1:
                    continue
                
                if not merged_entity.route_id or not re.match(route_filter, merged_entity.route_id):
                    continue
               
                # If the train is specified as not assigned, don't bother processing
                if not merged_entity.is_assigned:
                    continue
                
                # If the train is stopped at a station we're looking for, set that
                if merged_entity.is_stopped and merged_entity.is_stop_match(stop_filter, merged_entity.current_stop_id) and\
                    merged_entity.current_stop_id in stop_id_dict:
                    time_idx = merged_entity.time_raw - start_min
                    stop_idx = stop_id_dict.get(merged_entity.current_stop_id, -1)
                    if stop_idx >= 0:
                        self.stop_dict[merged_entity.train_id_str].append(merged_entity.current_stop_id)
                        self.time_dict[merged_entity.train_id_str].append(merged_entity.current_stop_time.tz_convert('US/Eastern'))
                    else:
                        new_stop_ids.add(merged_entity.current_stop_id)

                next_scheduled_arrival_np = train_schedule_np_dict[merged_entity.train_id_str]
                time_idx = merged_entity.time_raw - start_min
                stop_idx = stop_id_dict.get(merged_entity.current_stop_id, -1)

                if stop_idx >= 0:
                    next_scheduled_arrival_np[time_idx, stop_idx] = \
                        merged_entity.current_stop_time_raw
                else:
                    new_stop_ids.add(merged_entity.current_stop_id)

                # Iterate through next stops and see when then next train is scheduled to arrive
                if merged_entity.n_upcoming_stops > 0:
                    for upcoming_idx in range(merged_entity.n_upcoming_stops):
                        if merged_entity.is_stop_match(stop_filter, merged_entity.upcoming_stop_id(upcoming_idx)):
                            stop_idx = stop_id_dict.get(merged_entity.upcoming_stop_id(upcoming_idx), -1)

                            if stop_idx >= 0:
                                next_scheduled_arrival_np[time_idx, stop_idx] = \
                                    merged_entity.upcoming_stop_time_raw(upcoming_idx)
                            else:
                                new_stop_ids.add(merged_entity.upcoming_stop_id(upcoming_idx))

        if verbose:
            bar.finish()
        print("New stops:\n{}".format(new_stop_ids))
            
        self.next_train_df = pd.DataFrame(next_train_np, index=range(start_min, end_min), columns=stop_id_index)

        self.next_train_df = self.next_train_df.sort_index()
        self.next_train_df.index = self.next_train_df.index.map(lambda x: pd.to_datetime(x, unit='m', utc=True)).tz_convert('US/Eastern')

        # Create a dataframe describing each train's expected arrival time at a given station
        self.train_schedule_dict = dict()
        for train_id, train_schedule_np in train_schedule_np_dict.items():
            train_schedule_df = pd.DataFrame(train_schedule_np, index=range(start_min, end_min), columns=stop_id_index)
            train_schedule_df = train_schedule_df.sort_index()
            self.train_schedule_dict[train_id] = train_schedule_df

        self.next_scheduled_arrival_df = pd.concat(self.train_schedule_dict.values(), axis=1,
                                                   keys=self.train_schedule_dict.keys()).stack()


#        if schedule:
#            ret_dict['schedule_df'] = pd.DataFrame.from_dict(self.train_dict)

        return None



