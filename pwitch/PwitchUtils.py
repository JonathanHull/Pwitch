import os
import json

def parent_dir(path):
    """Returns parent directory of path"""
    return os.path.abspath(os.path.join(path, os.pardir))

def load_json(path):
    """Returns dictionary from json path"""
    with open(path, "r") as w:
        adict = json.open(w)
    return adict
