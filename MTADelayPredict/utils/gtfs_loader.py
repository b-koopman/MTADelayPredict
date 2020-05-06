from MTADelayPredict.utils.utils import grouper
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

def gtfs_datetime(filename):
    import re
    import pandas as pd
    prog = re.compile(r'^gtfs_.+_(?P<year>[0-9]{4})(?P<month>[0-9]{2})(?P<day>[0-9]{2})_(?P<hour>[0-9]{2})(?P<minute>[0-9]{2})(?P<second>[0-9]{2})\.gtfs$')
    m = prog.match(filename)
    if m:
        return pd.Timestamp(**{k:int(v) for k,v in m.groupdict().items()})
    else:
        raise ValueError("filename {} does not fit expected format".format(filename))
    
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
            
        yield((trip_entity, vehicle_entity))


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
    
    def load_range(self, start_date, end_date, stop_filter='.*', verbose=False):
        """
        Load files for a given date range and return the resulting dataframe.
        This new data replaces any existing loaded data.
        
        If verbose, it will display a progress bar
        """
        import re
        import os
        import google.protobuf.message as message
        
        if verbose:
            import progressbar
        
        # Get list of files
        gtfs_files = self.list_files(start_date, end_date)
        stopped_at_df = pd.DataFrame()
        next_scheduled_arrival_df = pd.DataFrame()
        next_train_df = pd.DataFrame()
        
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
                bar.update(i+1, entries=stopped_at_df.shape[0], decode_errors=fails)

            # TODO: This will be a lot cleaner once the entity data is broken into a separate class
            for trip_entity,vehicle_entity in get_entities(msg):
                if not vehicle_entity.vehicle.trip.Extensions[nyct_subway_pb2.nyct_trip_descriptor].is_assigned:
                    continue

                trip_direction = vehicle_entity.vehicle.trip.Extensions[nyct_subway_pb2.nyct_trip_descriptor].direction
                route_id = vehicle_entity.vehicle.trip.route_id
                entity_time = pd.to_datetime(vehicle_entity.vehicle.timestamp, unit='s', utc=True)
                
                # If a vehicle is stopped at the desired stop, capture it
                if vehicle_entity.vehicle.current_status == gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus.STOPPED_AT:
                    # Current stop is always the first stop_update in the trip entity as per: 
                    # http://datamine.mta.info/sites/all/files/pdfs/GTFS-Realtime-NYC-Subway%20version%201%20dated%207%20Sep.pdf
                    # Therefore, if a train is "STOPPED_AT", we can get the current stop_id this way
                    if len(trip_entity.trip_update.stop_time_update) == 0:
                        if verbose:
                            print("Skipped vehicle entity, no stop times {}".format(trip_entity.trip_update))
                        continue
                    current_stop = trip_entity.trip_update.stop_time_update[0]
                    
                    # NOTE: Sometimes the arrival times for the current stop don't match up, this is a bit weird, look into this
                    #    assert current_stop.arrival.time <= vehicle_entity.vehicle.timestamp

                    if re.match(stop_filter, current_stop.stop_id):
                        current_train_id = vehicle_entity.vehicle.trip.Extensions[nyct_subway_pb2.nyct_trip_descriptor].train_id
                        stopped_at_df.loc[entity_time, current_stop.stop_id] = current_train_id

                    if len(trip_entity.trip_update.stop_time_update) > 1:
                        next_stop = trip_entity.trip_update.stop_time_update[1]
                    else:
                        next_stop = None
                else:
                    next_stop = trip_entity.trip_update.stop_time_update[0]

                # Extract next train, and when it thinks it will arrive
                if next_stop:
                    if re.match(stop_filter, next_stop.stop_id):
                        # If multiple trains have a stop_id as their next stop, take whichever one thinks it is closest
                        if entity_time in next_scheduled_arrival_df.index and next_stop.stop_id in next_scheduled_arrival_df.columns:
                            next_scheduled_arrival_df.loc[entity_time, next_stop.stop_id] = \
                                min(next_scheduled_arrival_df.loc[entity_time, next_stop.stop_id], pd.to_datetime(next_stop.arrival.time, unit='s', utc=True))
                        else:
                            next_scheduled_arrival_df.loc[entity_time, next_stop.stop_id] = \
                                pd.to_datetime(next_stop.arrival.time, unit='s', utc=True)
                        next_train_df.loc[entity_time, next_stop.stop_id] = \
                            trip_entity.trip_update.trip.Extensions[nyct_subway_pb2.nyct_trip_descriptor].train_id
        if verbose:
            bar.finish()

        stopped_at_df.index = stopped_at_df.index.tz_convert('US/Eastern')
        next_train_df.index = next_train_df.index.tz_convert('US/Eastern')
        next_scheduled_arrival_df.index = next_scheduled_arrival_df.index.tz_convert('US/Eastern')
        stopped_at_df.sort_index(inplace=True)
        next_train_df.sort_index(inplace=True)
        next_scheduled_arrival_df.sort_index(inplace=True)
        self.stopped_at_df = stopped_at_df
        self.next_train_df = next_train_df
        self.next_scheduled_arrival_df = next_scheduled_arrival_df
        
        return {'stopped_at':self.stopped_at_df, \
                'next_train':self.next_train_df, \
                'next_scheduled_arrival': self.next_scheduled_arrival_df}
 