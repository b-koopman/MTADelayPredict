class Stop:
    """
    Encapsulate stop arithmetic to make it easier to figure out how many stops away we are
    There is an assumption that if a stop appears in another stop's stop
    """

    def _validate(self, other_stop):
        # Make sure that the two stops are for the same direction trains,
        # this should also be covered by searching dict, but this error message is more helpful
        # For some reason, even East/West trains always use N/S designators, so this should generally be pretty simple
        if self.stop_id[-1] != other_stop.stop_id[-1]:
            raise ValueError("Cannot compare {} to self ({}), "
                             "directions are different".format(other_stop.stop_id, self.stop_id))

        if other_stop.stop_id not in self.subway_line.stop_indices:
            raise ValueError("Stop {} not found in stop_list {}".format(other_stop, self.subway_line.stop_list))

    def __init__(self, stop_id, subway_line):
        """
        stop_id: fully specified stop, including direction, such as 'R16N'
        stop_list: Fully specified list of stops 
        """
        self.stop_id = stop_id
        self.stop_idx = subway_line.stop_indices[stop_id]
        self.subway_line = subway_line

    def __gt__(self, other):
        self._validate(other)
        return self.stop_idx > other.stop_idx

    def __lt__(self, other):
        self._validate(other)
        return self.stop_idx < other.stop_idx

    def __eq__(self, other):
        self._validate(other)
        return self.stop_idx == other.stop_idx

    def __neq__(self, other):
        self._validate(other)
        return self.stop_idx == other.stop_idx

    def __ge__(self, other):
        self._validate(other)
        return self.stop_idx >= other.stop_idx

    def __le__(self, other):
        self._validate(other)
        return self.stop_idx <= other.stop_idx

    def __add__(self, val):
        """
        increase stop by integer value "val"
        it will saturate at the end of the line to make arithmetic easier
        """
        if not isinstance(val, int):
            raise ValueError("Can only increase stop by an integer index, got {}".format(type(val)))
        if val < 0:
            return self.__sub__(-val)
        new_idx = self.stop_idx + val
        new_idx = min(new_idx, len(self.subway_line.stop_list) - 1)
        return self.subway_line.stop_from_idx(new_idx)

    def __sub__(self, val):
        """
        decrease stop by integer value "val"
        it will saturate at the end of the line to make arithmetic easier
        """
        if isinstance(val, int):
            raise ValueError("Can only decrease stop by an integer index got {}".format(type(val)))
        if val < 0:
            return self.__add__(-val)
        new_idx = self.stop_idx - val
        new_idx = max(new_idx, 0)
        return self.subway_line.stop_from_idx(new_idx)
