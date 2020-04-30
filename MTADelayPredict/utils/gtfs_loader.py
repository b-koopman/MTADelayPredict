
def gtfs_datetime(filename):
    import re
    import pandas as pd
    prog = re.compile(r'^gtfs_.+_(?P<year>[0-9]{4})(?P<month>[0-9]{2})(?P<day>[0-9]{2})_(?P<hour>[0-9]{2})(?P<minute>[0-9]{2})(?P<second>[0-9]{2})\.gtfs$')
    m = prog.match(filename)
    if m:
        return pd.Timestamp(**{k:int(v) for k,v in m.groupdict().items()})
    else:
        raise ValueError("filename {} does not fit expected format".format(filename))
    
    
class GTFSLoader: 
    """
    Class to iterate through gtfs files across a date range for a given train_line
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
    
    def files(self, start_date, end_date):
        """
        get all the globs 
        """
        import pandas as pd
        import glob
        import os
        
        drange = pd.date_range(start_date, end_date, freq='D')
        
        file_list = []
        
        for date in drange:
            yyyymm = str(date.year * 100 + date.month)
            yyyymmdd = str(date.year * 10000 + date.month * 100 + date.day)
            filename = 'gtfs_{}_{}_*.gtfs'.format(self.train_line, yyyymmdd)
            daily_files = glob.glob(os.path.join(self.data_dir, yyyymm, yyyymmdd, filename))
            daily_files = [ f for f in daily_files if (gtfs_datetime(f) >= start_date and gtfs_datetime(f) <= end_date) ]
            if len(daily_files) == 0:
                print("WARNING: no files found for {}".format(yyyymmdd))
            file_list += daily_files
        
        return file_list
    