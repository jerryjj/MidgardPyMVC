from midgardmvc.components.interfaces import IComponent, IPurecodeComponent
from zope.interface import implements

#import ConfigParser
import os
from pkg_resources import resource_string, resource_filename

import midgardmvc.components.configloader

def load_config(path):
    if not os.path.exists(path):
        return dict()

    return midgardmvc.components.configloader.load(file(path, 'r'))

class ComponentBase(object):
    implements(IComponent)
    __name__ = __name__
    __purecode__ = False
    
    __routes__ = []
    __routes_prefix__ = None
    __config_dir__ = None
    __templates_dir__ = None
    __static_files__ = None
    
    def __init__(self, config=None):
        self.override_config = config
        self.config = dict()
        
        self._config_contexts = dict()
        
        self.component_root = self.resolveComponentPath('/')
        self.__config_dir__ = os.path.join(self.component_root, 'config')
        self.__templates_dir__ = os.path.join(self.component_root, 'templates')
        self.__static_files__ = os.path.join(self.component_root, 'public')
        
        self.loadConfiguration()
        
        self.initialize()
    
    def resolveComponentPath(self, dir_name):
        return resource_filename(self.__name__, dir_name)
    
    def resolveComponentResource(self, resource):
        return resource_string(self.__name__, resource)
    
    def loadConfiguration(self, name="default"):
        config_path = os.path.join(self.__config_dir__, name + ".yml")
        
        if not os.path.exists(config_path):
            if self.override_config:
                self.config = midgardmvc.components.configloader.merge(self.config, self.override_config)
            return
        
        self._config_contexts[name] = load_config(config_path)
        self.config = midgardmvc.components.configloader.merge(self.config, self._config_contexts[name])
        
        if self.override_config:
            self.config = midgardmvc.components.configloader.merge(self.config, self.override_config)
        
    def prepareRoutes(self):
        pass

class PurecodeComponentBase(ComponentBase):
    implements(IPurecodeComponent)
    
    __purecode__ = True

# import setuptools.Command
# 
# def install_statics(Command):
#     """This command install component statics to MVC public folder"""    
# 
#     description = "Install statics"
#     user_options = tuple()
#     
#     def initialize_options(self):
#         """init options"""
#         pass
# 
#     def finalize_options(self):
#         """finalize options"""
#         pass
# 
#     def run(self):
#         """runner"""
#         pass