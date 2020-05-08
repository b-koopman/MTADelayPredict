from MTADelayPredict.utils.utils import grouper, gtfs_datetime
from MTADelayPredict.utils.merged_entity import MergedEntity
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
        self.data_dir = data_dir
        self.train_line = train_line
    
        self.stopped_at_df = pd.DataFrame()
        self.next_train_df = pd.DataFrame()
        self.next_scheduled_arrival_df =  pd.DataFrame()
        
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
            daily_files = glob.glob(os.path.join(self.data_dir, yyyymm, yyyymmdd, filename))
            daily_files = [ f for f in daily_files if (gtfs_datetime(os.path.basename(f)) >= start_date and gtfs_datetime(os.path.basename(f)) <= end_date) ]
#            if len(daily_files) == 0:
#                print("WARNING: no files found for {} in {}".format(yyyymmdd, os.path.join(self.data_dir, yyyymm, yyyymmdd, filename)))
            file_list += daily_files
        
        return file_list
    
    def load_range(self, start_date, end_date, stop_filter='.*', route_filter='.*', verbose=False):
        """
        Load files for a given date range and return the resulting dataframe.
        This new data replaces any existing loaded data.
        
        If verbose, it will display a progress bar
        """
        import re
        import os
        import google.protobuf.message as message
        import numpy as np
        
        if verbose:
            import progressbar
        
        # Get list of files
        gtfs_files = self.list_files(start_date, end_date)
        
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
                if not re.match(route_filter, merged_entity.route_id):
                    continue
               
                # If the train is specified as not assigned, don't bother processing
                if not merged_entity.is_assigned:
                    continue
                
                # If the train is stopped at a station we're looking for, set that
                if merged_entity.is_stopped and merged_entity.is_stop_match(stop_filter, merged_entity.current_stop_id):
                    self.stopped_at_df.loc[merged_entity.time, merged_entity.current_stop_id] = merged_entity.train_id
                
                # If there is a next stop specified, set the next arrival time for that station
                # Sometimes there might be multiple trains scheduled to arrive somewhere next, so use the min
                if merged_entity.next_stop_id and merged_entity.is_stop_match(stop_filter, merged_entity.next_stop_id):
                    if merged_entity.time in self.next_scheduled_arrival_df.index and merged_entity.next_stop_id in self.next_scheduled_arrival_df.columns:
                        current_val = self.next_scheduled_arrival_df.loc[merged_entity.time, merged_entity.next_stop_id]
                        new_val = pd.to_datetime(merged_entity.next_stop_time, unit='s', utc=True)
                        
                        if isinstance(current_val, pd.Timestamp) and new_val < current_val:
                            self.next_train_df.loc[merged_entity.time, merged_entity.next_stop_id] = merged_entity.train_id
                            self.next_scheduled_arrival_df.loc[merged_entity.time, merged_entity.next_stop_id] = new_val
                    else:
                        self.next_train_df.loc[merged_entity.time, merged_entity.next_stop_id] = merged_entity.train_id
                        self.next_scheduled_arrival_df.loc[merged_entity.time, merged_entity.next_stop_id] = \
                            pd.to_datetime(merged_entity.next_stop_time, unit='s', utc=True)
                
                
        if verbose:
            bar.finish()

        self.stopped_at_df.index = self.stopped_at_df.index.tz_convert('US/Eastern')
        self.next_train_df.index = self.next_train_df.index.tz_convert('US/Eastern')
        self.next_scheduled_arrival_df.index = self.next_scheduled_arrival_df.index.tz_convert('US/Eastern')
        self.stopped_at_df.sort_index(inplace=True)
        self.next_train_df.sort_index(inplace=True)
        self.next_scheduled_arrival_df.sort_index(inplace=True)
        
        return {'stopped_at':self.stopped_at_df, \
                'next_train_id':self.next_train_df, \
                'next_scheduled_arrival': self.next_scheduled_arrival_df}
 