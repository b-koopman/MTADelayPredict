from nose.tools import raises, assert_raises, with_setup
from MTADelayPredict.subway_line import SubwayLine
from MTADelayPredict.stop import Stop

class testStop():
    @classmethod
    def setup_class(cls):
        cls.stop_list = ['R1N', 'R2N', 'W3N']
        cls.test_line = SubwayLine(cls.stop_list)

    @classmethod
    def teardown_class(cls):
        pass

    def test_stop_basic_arithmetic(self):
        """
        Test basic arithmetic for subway stops
        """
        test_stop = self.test_line.stop('R1N')

        # Cannot add two stops together
        assert_raises(ValueError, test_stop.__add__, test_stop)

        # Simple addition
        new_stop = test_stop + 1
        assert new_stop.stop_id == 'R2N'
        assert new_stop.stop_idx == 1

        # Simple subtract
        new_stop -= 1
        assert new_stop.stop_id == 'R1N'
        assert new_stop.stop_idx == 0

        # Find difference between two stops

    def test_stop_overflow_arithmetic(self):
        """
        What happens when there are overflows/saturations in arithmetic
        """
        test_stop = self.test_line.stop('R1N')

        test_stop -= 1
        assert test_stop.stop_idx == 0

        test_stop += 50
        assert test_stop.stop_idx == len(self.stop_list) - 1
        assert test_stop.stop_id == 'W3N'


    def test_stop_comparison(self):
        """
        Stop comparisons
        """
        # Do some basic comparisons for our stops
        stop1 = self.test_line.stop('R1N')
        stop2 = self.test_line.stop('W3N')
        assert stop1 < stop2
        assert stop2 > stop1
        assert stop1 != stop2
        assert stop1 == stop1

        # Compare stops from a second line
        test_line2 = SubwayLine(self.stop_list)
        stop3 = test_line2.stop('W3N')
        assert stop1 < stop3
        assert stop3 > stop1
        assert stop1 != stop3
        # Different lines, but same stop_id
        assert stop2 == stop3


    def test_stop_iteration(self):
        """
        Iterate through the stops in a line
        """
        test_stop = self.test_line.begin()

        visited_stops = [test_stop.stop_id]
        while test_stop != self.test_line.end():
            test_stop += 1
            visited_stops.append(test_stop.stop_id)

        assert all([sid1 == sid2 for sid1, sid2 in zip(self.stop_list, visited_stops)])

