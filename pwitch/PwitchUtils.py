import os

def parent_dir(path):
    """Returns parent directory of path"""
    return os.path.abspath(os.path.join(path, os.pardir))
