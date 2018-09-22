import os
import json

from datetime import datetime

def parent_dir(path):
    """Returns parent directory of path"""
    return os.path.abspath(os.path.join(path, os.pardir))

def load_json(path):
    """Returns dictionary from json path"""
    with open(path, "r") as w:
        adict = json.open(w)
    return adict

def get_datetime():
    """Returns formatted current utc datetime."""
    dt = datetime.utcnow()
    date = ",".join(str(i) for i in dt.timetuple()[:3]).replace(",","-")
    time = ":".join(str(i) for i in dt.timetuple()[3:6])
    d = " ".join([date,time])
    return d
