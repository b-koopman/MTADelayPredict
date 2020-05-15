from MTADelayPredict.utils import stop_info

def test_stopid2name():
    times_square = stop_info.stopid2name('R16N')
    assert times_square == 'Times Sq - 42 St'

    times_square = stop_info.stopid2name('R16')
    assert times_square == 'Times Sq - 42 St'

    times_square = stop_info.stopid2name('R16S')
    assert times_square == 'Times Sq - 42 St'

    times_square = stop_info.stopid2name('BOGUS')
    assert times_square == None

# Ordered in northbound order
N_STOP_LIST = ['D43N', 'N10N', 'N09N', 'N08N', 'N07N', 'N06N', 'N05N', 'N04N', 'N03N', 'N02N', 'R41N', 'R40N', 'R39N', \
               'R36N', 'R35N', 'R34N', 'R33N', 'R32N', 'R31N', 'R30N', 'R29N', 'R28N', 'R27N', 'R26N', 'R25N', 'R24N', \
               'R23N', 'R22N', 'R21N', 'R20N', 'R19N', 'R18N', 'R17N', 'R16N', 'R15N', 'R14N', 'R13N', 'R11N', 'R09N', \
               'R08N', 'R06N', 'R05N', 'R04N', 'R03N', 'R01N']

def test_name2stopids():
    stop_name = "Times Sq - 42 St"
    direction = 'N'
    stop_ids = stop_info.name2stop_ids(stop_name, N_STOP_LIST)
    assert stop_ids.shape == (1,)
