#!/usr/bin/env python3
"""
Tool for converting between stop_id and human readable station names
"""
import argparse
import sys
import os

# For now, assume this lives in, or gets dist'd with the same directory structure
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(os.path.join('mta_stop.py')))))

# For now, we only care about the Northbound N Train
from MTADelayPredict.subway_line import N_STOP_LIST
from MTADelayPredict.utils import stop_info

def main(args):
    if args.station_name and args.stop_id:
        raise ValueError("Can only use station_name or stop_id, not both")
    if args.station_name:
        return stop_info.name2stop_ids(args.station_name, N_STOP_LIST)
    else:
        return stop_info.stop_id2name(args.stop_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert between stop_ids and station names')
    parser.add_argument('-i', '--stop_id', type=str, default=None,
                        help='stop_id to convert to human readable name')
    parser.add_argument('-n', '--station_name', type=str, default=None,
                        help='station_name to convert to stop_id')
    args = parser.parse_args()
    if not args:
        raise ValueError("No input specified")
    retval = main(args)
    print(retval)
