from pkg_resources import iter_entry_points

import logging
log = logging.getLogger(__name__)

_components = {}

class ComponentNotLoaded(Exception): pass

def load_all():
    global _components
    
    for entry_point in iter_entry_points(group='midgardmvc.component', name=None):
        log.debug("Loading component: %s" % entry_point.name)
        
        if not _components.has_key(entry_point.name):
            _components[entry_point.name] = _load_instance(entry_point)
    
def load(name):
    global _components
    
    if not _components.has_key(name):
        for entry_point in iter_entry_points(group='midgardmvc.component', name=name):
            log.debug("Loading component: %s" % entry_point.name)
            _components[entry_point.name] = _load_instance(entry_point)
    
    return _components[name]

def _load_instance(entry_point):
    cls = entry_point.load()
    instance = cls(component_config={})
    
    if not instance.__purecode__:
        instance.loadConfiguration()
        instance.prepareRoutes()        
    
    return instance

def update_paths(paths):        
    for name, component in _components.iteritems():
        if component.__purecode__:
            continue
        
        #Update template paths
        if component.__templates_dir__:
            paths["templates"].append(component.__templates_dir__)

        #Update static file paths
        if component.__static_files__:
            paths["static_files"].append(component.__static_files__)
        
    return paths

def connect_routes(map):
    for name, component in _components.iteritems():
        if component.__purecode__:
            continue
        map.extend(component.__routes__, component.__routes_prefix__)
    
    return map

def get(name):
    if not _components.has_key(name):
        raise ComponentNotLoaded("Component not yet loaded!")
    
    return _components[name]