from MTADelayPredict.stop import Stop

# Ordered in northbound order
N_STOP_LIST = ['D43N', 'N10N', 'N09N', 'N08N', 'N07N', 'N06N', 'N05N', 'N04N', 'N03N', 'N02N', 'R41N', 'R40N', 'R39N', \
               'R36N', 'R35N', 'R34N', 'R33N', 'R32N', 'R31N', 'R30N', 'R29N', 'R28N', 'R27N', 'R26N', 'R25N', 'R24N', \
               'R23N', 'R22N', 'R21N', 'R20N', 'R19N', 'R18N', 'R17N', 'R16N', 'R15N', 'R14N', 'R13N', 'R11N', 'R09N', \
               'R08N', 'R06N', 'R05N', 'R04N', 'R03N', 'R01N']

class SubwayLine():
    def __init__(self, stop_list):
        if len(stop_list) == 0:
            raise ValueError("Empty stop list")
        self.stop_indices = dict()
        self.stop_list = stop_list

        # Create lookup of which stop is at which position
        direction = None
        for i, stop_id in enumerate(stop_list):
            if direction and stop_id[-1] != direction:
                raise ValueError("Inconsistent stop_id directions,"
                                 "all stops must belong to the same direction line")
            direction = stop_id[-1]
            self.stop_indices[stop_id] = i
        if not (direction == 'N' or direction == 'S'):
            raise ValueError("Invalid direction in stop_list {}, got {}"
                             "they need to be fully qualified e.g. \"R16N\"".format(stop_list, direction))

    def stop(self, stop_id):
        if stop_id not in self.stop_indices:
            raise ValueError("StopID {} not found in specified stop_list {}".format(stop_id, self.stop_list))
        return Stop(stop_id, self)

    def stop_from_idx(self, stop_idx):
        if stop_idx >= len(self.stop_list) or stop_idx < 0:
            raise IndexError("index {} exceeds stop list bounds".format(stop_idx))
        return Stop(self.stop_list[stop_idx], self)

    def begin(self):
        return Stop(self.stop_list[0], self)

    def end(self):
        return Stop(self.stop_list[-1], self)

    def stop_idx(self, stop_id):
        """
        Get the index of a stop_id within a subway line
        """
        if stop_id not in self.stop_indices:
            raise ValueError("{} not in SubwayLine's stops".format(stop_id))
        return self.stop_indices[stop_id]

