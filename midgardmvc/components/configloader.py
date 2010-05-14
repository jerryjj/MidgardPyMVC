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
    if not isinstance(original, dict):
        original = dict()
    
    if not isinstance(override, dict):
        return override
    
    for key, value in override.iteritems():
        if isinstance(value, dict):
            original[key] = merge(original.get(key, dict()), value)
        else:
            original[key] = value
    
    return original