from pkg_resources import iter_entry_points
import os
import logging
log = logging.getLogger(__name__)

from pkg_resources import resource_string, resource_filename
from midgardmvc.components.base import load_config

_components = {}

class ComponentNotLoaded(Exception): pass

_project_root = None

def load_all(global_conf):
    global _project_root, _components
    
    _project_root = global_conf["here"]
    
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

    override_config = None    
    override_config_path = os.path.join(os.path.abspath(_project_root + '/config/'), entry_point.name + ".yml")
    
    if os.path.exists(override_config_path):
        override_config = load_config(override_config_path)
    
    instance = cls(component_config=override_config)
    
    if not instance.__purecode__:
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
            
        #Update controllers paths
        controllers_path = os.path.abspath(component.component_root + "/../../controllers/")
        if os.path.exists(controllers_path):
            paths["controllers"].append(controllers_path)
        
    return paths

def connect_routes(map):
    for name, component in _components.iteritems():
        if component.__purecode__:
            continue
        map.extend(component.__routes__, component.__routes_prefix__)
    
    return map
    
def connect_components_to_environ(environ):
    for name in _components:
        environ[name] = _components[name]
    
    return environ

def get(name):
    if not _components.has_key(name):
        raise ComponentNotLoaded("Component %s not yet loaded!" % name)
    
    return _components[name]

def get_config(name):
    if not _components.has_key(name):
        raise ComponentNotLoaded("Component %s not yet loaded!" % name)
    
    return _components[name].config    