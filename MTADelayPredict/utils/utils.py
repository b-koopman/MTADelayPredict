# Retrieved from: https://docs.python.org/3/library/itertools.html#itertools.groupby 4/29/2020
from itertools import zip_longest

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def gtfs_datetime(filename):
    import re
    import pandas as pd
    prog = re.compile(r'^gtfs_.+_(?P<year>[0-9]{4})(?P<month>[0-9]{2})(?P<day>[0-9]{2})_(?P<hour>[0-9]{2})(?P<minute>[0-9]{2})(?P<second>[0-9]{2})\.gtfs$')
    m = prog.match(filename)
    if m:
        return pd.Timestamp(**{k:int(v) for k,v in m.groupdict().items()})
    else:
        raise ValueError("filename {} does not fit expected format".format(filename))