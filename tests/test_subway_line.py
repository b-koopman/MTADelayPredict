from nose.tools import raises, assert_raises
from MTADelayPredict.subway_line import SubwayLine, N_STOP_LIST

@raises(ValueError)
def test_wrong_direction_line():
    bad_line = SubwayLine(['R1N', 'R2S'])

@raises(ValueError)
def test_underspecified_stops():
    bad_line = SubwayLine(['R1', 'R2'])

def test_stop_idx():
    test_line = SubwayLine(['R16N', 'R15N'])
    assert test_line.stop_idx('R16N') == 0

def test_stop_create():
    # Test creation of new stops
    stop_list = ['R1N', 'R2N', 'W3N']
    test_line = SubwayLine(stop_list)

    assert_raises(ValueError, test_line.stop, '1N')
    test_stop = test_line.stop('R1N')
    assert test_stop.stop_id == 'R1N'
    assert test_stop.stop_idx == 0

    assert_raises(IndexError, test_line.stop_from_idx, 5)
    assert_raises(IndexError, test_line.stop_from_idx, -1)

    test_stop = test_line.stop_from_idx(2)
    assert test_stop.stop_id == 'W3N'
    assert test_stop.stop_idx == 2
