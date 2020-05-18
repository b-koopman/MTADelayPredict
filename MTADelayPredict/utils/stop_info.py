from functools import lru_cache

class StopFile:
    """
    Singleton class for loading stop file once, we really should only have one stop file at a time
    """

    class __StopFile:
        def __init__(self, file_dir):
            import pandas as pd
            self.file_dir = file_dir
            self.df = pd.read_csv(file_dir + '/stops.txt')
            self.df['CleanStopName'] = self.df.stop_name.map(normalize_name)

    instance = None

    def __init__(self, file_dir=None):
        import os
        if file_dir is None:
            proj_dir = os.path.dirname(os.path.dirname(os.path.realpath(os.path.basename(__file__))))
            file_dir = os.path.join(proj_dir, 'data/raw/status/google_transit')

        if (StopFile.instance is None) or (StopFile.instance.file_dir != file_dir):
            StopFile.instance = StopFile.__StopFile(file_dir)

    def __getattr__(self, name):
        return getattr(self.instance, name)

@lru_cache()
def stop_id2name(stop_id):
    df = StopFile().df
    try:
        names = df.stop_name[df.stop_id.str.match(stop_id)]
        return names.iloc[0]
    except IndexError:
        return None

    return df.stop_name.iloc[idx]

def normalize_name(stop_name):
    import re

    # Remove any borough annotations
    clean_name = re.sub(r' ?\(.*\)', '', stop_name)

    clean_name = clean_name.lower()
    clean_name = re.sub('[^0-9a-z]+', '', clean_name)

    return clean_name

def name2stop_ids(stop_name, stop_list=None):
    """
    :param stop_name: Name of the stop
    :return: pandas.Series of possibly matching stop_ids
    """
    df = StopFile().df
    stop_ids = df.stop_id[df['CleanStopName'].str.match(normalize_name(stop_name))]
    if stop_list:
        stop_set = set(stop_list)
        stop_ids = stop_ids[stop_ids.map(lambda x: x in stop_set)]
    return stop_ids
