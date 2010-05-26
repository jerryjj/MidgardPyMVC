import os, re

from UserDict import UserDict

def asBool(value):
    if isinstance(value, basestring):
        return value.lower() in ('yes', 'true', '1')
    return value

class odict(UserDict):
    def __init__(self, dict = None):
        self._keys = []
        UserDict.__init__(self, dict)

    def __delitem__(self, key):
        UserDict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        UserDict.__setitem__(self, key, item)
        if key not in self._keys: self._keys.append(key)

    def clear(self):
        UserDict.clear(self)
        self._keys = []

    def copy(self):
        dict = UserDict.copy(self)
        dict._keys = self._keys[:]
        return dict

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        val = self[key]
        del self[key]

        return (key, val)

    def setdefault(self, key, failobj = None):
        UserDict.setdefault(self, key, failobj)
        if key not in self._keys: self._keys.append(key)

    def update(self, dict):
        UserDict.update(self, dict)
        for key in dict.keys():
            if key not in self._keys: self._keys.append(key)

    def values(self):
        return map(self.get, self._keys)

def controller_scan(directories=None):
    """Scan a list of directories for python files and use them as controllers"""
    if directories is None:
        return []
    
    def find_controllers(dirname, prefix=''):
        """Locate controllers in a directory"""
        controllers = []
        for fname in os.listdir(dirname):
            filename = os.path.join(dirname, fname)
            
            if os.path.isfile(filename) and re.match('^[^_]{1,1}.*\.py$', fname):
                controllers.append(prefix + fname[:-3])
            elif os.path.isdir(filename):
                controllers.extend(find_controllers(filename, 
                                                    prefix=prefix+fname+'/'))
        return controllers
    
    def longest_first(fst, lst):
        """Compare the length of one string to another, shortest goes first"""
        return cmp(len(lst), len(fst))
    
    controllers = []
    for directory in directories:    
        controllers = controllers + find_controllers(directory)
    
    controllers.sort(longest_first)
    
    return controllers