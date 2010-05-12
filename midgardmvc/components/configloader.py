from yaml import load as yaml_load, dump as yaml_dump
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def load(stream):
    return yaml_load(stream, Loader=Loader)    

def dump(data, stream=None):
    return yaml_dump(data, stream, Dumper=Dumper)

def merge(original, override):
    return original.update(override)