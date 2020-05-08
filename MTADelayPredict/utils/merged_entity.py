import pandas as pd
from functools import lru_cache

# Load in the protobuf APIs
try:
    import MTADelayPredict.protobuf.nyct_subway_pb2 as nyct_subway_pb2
except ImportError:
    raise ImportError('nyct_subway_pb2 not found, make sure protobuf is compiled, see DataExploration.ipynb')
try:
    import MTADelayPredict.protobuf.gtfs_realtime_pb2 as gtfs_realtime_pb2
except ImportError:
    raise ImportError('gtfs_realtime_pb2 not found, make sure protobuf is compiled, see DataExploration.ipynb')

class MergedEntity:
    """
    Class that aggregates relevant train data from a pair of vehicle and trip entities
    Much of this is convenience functions for accessing the two entities
    """
    def __init__(self, trip_entity, vehicle_entity):
        self.trip_entity = trip_entity
        self.vehicle_entity = vehicle_entity
        
    @property
    @lru_cache(1)
    def is_assigned(self):
        """
        If a train is assigned.
        Sometimes this field is dropped, in these cases assume that the vehicle is assigned.  If not, we should be able to handle the data anyways
        """
        if not self.vehicle_entity.vehicle.trip.Extensions[nyct_subway_pb2.nyct_trip_descriptor].HasField('is_assigned'):
            return True
        return self.vehicle_entity.vehicle.trip.Extensions[nyct_subway_pb2.nyct_trip_descriptor].is_assigned
    
    @property
    @lru_cache(1)
    def is_stopped(self):
        """
        If a train has a stop status, use it, otherwise assume it is stopped
        """
        if self.vehicle_entity.vehicle.HasField('current_status'):
            return self.vehicle_entity.vehicle.current_status == gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus.STOPPED_AT
        else:
            return self._current_stop() != None
    
    @lru_cache(1)
    def _current_stop(self):            
        # Current stop is always the first stop_update in the trip entity as per: 
        # http://datamine.mta.info/sites/all/files/pdfs/GTFS-Realtime-NYC-Subway%20version%201%20dated%207%20Sep.pdf
        # Therefore, if a train is "STOPPED_AT", we can get the current stop_id this way
        if len(self.trip_entity.trip_update.stop_time_update) < 1:
            return None
        return self.trip_entity.trip_update.stop_time_update[0]
    
    @property
    @lru_cache(1)
    def current_stop_id(self):
        if self._current_stop():
            return self._current_stop().stop_id
        else:
            return None
    
    @lru_cache(1)
    def _next_stop(self):
        """
        What stop is coming next?
        Position in the stop_time_update's is dictated by whether or not the train is stopped
        """
        if self.is_stopped:
            if len(self.trip_entity.trip_update.stop_time_update) < 2:
                return None            
            return self.trip_entity.trip_update.stop_time_update[1]
        else:
            if len(self.trip_entity.trip_update.stop_time_update) < 1:
                return None
    
    @property
    @lru_cache(1)
    def next_stop_id(self):
        if self._next_stop():
            return self._next_stop().stop_id
        else:
            return None
    
    @property
    @lru_cache(1)
    def next_stop_time(self):
        if self._next_stop():
            return self._next_stop().arrival.time
        else:
            return None
    
    @property
    @lru_cache(1)
    def time(self):
        return pd.to_datetime(self.vehicle_entity.vehicle.timestamp, unit='s', utc=True)
    
    @property
    @lru_cache(1)
    def train_id(self):
        return self.vehicle_entity.vehicle.trip.Extensions[nyct_subway_pb2.nyct_trip_descriptor].train_id
    
    @property
    @lru_cache(1)
    def route_id(self):
        return self.vehicle_entity.vehicle.trip.route_id
    
    def is_stop_match(self, stop_filter, stop_id):
        """
        Is this stop one of the ones we're looking for
        """
        import re
        return re.match(stop_filter, stop_id)