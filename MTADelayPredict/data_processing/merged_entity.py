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
            return self.trip_entity.trip_update.stop_time_update[0]

    @property
    @lru_cache(1)
    def next_stop_id(self):
        if self._next_stop():
            return self._next_stop().stop_id
        else:
            return None

    @property
    def n_upcoming_stops(self):
        if self.is_stopped:
            return len(self.trip_entity.trip_update.stop_time_update) - 1
        else:
            return len(self.trip_entity.trip_update.stop_time_update)

    @lru_cache(32)
    def _upcoming_stop(self, idx):
        """
        Return the upcoming stop at position "idx"
        :param idx: index of upcoming stop for this train, where idx < n_upcoming_stops
        :return: stop_id
        """
        if idx >= self.n_upcoming_stops:
            raise ValueError("index {} exceeds number of upcoming stops {}", idx, self.n_upcoming_stops)

        stop_idx = idx
        if self.is_stopped:
            stop_idx += 1

        return self.trip_entity.trip_update.stop_time_update[stop_idx]

    @lru_cache(32)
    def upcoming_stop_id(self, idx):
        stop = self._upcoming_stop(idx)
        return stop.stop_id

    @lru_cache(32)
    def upcoming_stop_time_raw(self, idx):
        stop = self._upcoming_stop(idx)
        return int(stop.arrival.time) // 60

    @property
    @lru_cache(1)
    def next_stop_time_raw(self):
        """
        Get UNIX time in minutes for the time this entity is scheduled to arrive at the next stop
        :return:
        """
        if self._next_stop():
            return int(self._next_stop().arrival.time) // 60
        else:
            return None
        
    @property
    @lru_cache(1)
    def current_stop_time_raw(self):
        """
        Get UNIX time in minutes for the time this entity was observed at the current stop
        :return:
        """
        if self._next_stop():
            return int(self._current_stop().arrival.time) // 60
        else:
            return 0
    
    @property
    @lru_cache(1)
    def time_raw(self):
        return int(self.vehicle_entity.vehicle.timestamp) // 60
        
    @property
    @lru_cache(1)
    def next_stop_time(self):
        if self._next_stop():
            pd.to_datetime(self.next_stop_time_raw, unit='m', utc=True)
        else:
            return None
        
    @property
    @lru_cache(1)
    def current_stop_time(self):
        return pd.to_datetime(self.current_stop_time_raw, unit='m', utc=True)
    
    @property
    @lru_cache(1)
    def time(self):
        return pd.to_datetime(self.time_raw, unit='m', utc=True)
    
    @property
    @lru_cache(1)
    def train_id_str(self):
        trip_descriptor = self.vehicle_entity.vehicle.trip.Extensions[nyct_subway_pb2.nyct_trip_descriptor]
        return trip_descriptor.train_id
    
    @property
    @lru_cache(1)
    def train_id(self):
        import re
        
        trip_descriptor = self.vehicle_entity.vehicle.trip.Extensions[nyct_subway_pb2.nyct_trip_descriptor]
        numerical_id = re.sub('[^0-9]', '', trip_descriptor.train_id)
    
        if numerical_id:
            return int(numerical_id)
        else:
            return np.nan           
    
    @property
    @lru_cache(1)
    def route_id(self):
        return self.vehicle_entity.vehicle.trip.route_id
    
    def is_stop_match(self, stop_filter, stop_id):
        """
        Is this stop one of the ones we're looking for
        """
        import re
        if stop_id:
            return re.match(stop_filter, stop_id)
        else:
            return False