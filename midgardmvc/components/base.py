from midgardmvc.components.interfaces import IComponent, IPurecodeComponent
from zope.interface import implements

import ConfigParser
import os
from pkg_resources import resource_string, resource_filename

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
        
        self.component_root = self.resolveComponentPath('/')
        self.__config_dir__ = os.path.join(self.component_root, 'config')
        self.__templates_dir__ = os.path.join(self.component_root, 'templates')
        self.__static_files__ = os.path.join(self.component_root, 'public')
        
        self.initialize()
    
    def resolveComponentPath(self, dir_name):
        return resource_filename(self.__name__, dir_name)
    
    def resolveComponentResource(self, resource):
        return resource_string(self.__name__, resource)
    
    def loadConfiguration(self, name="default"):
        config = ConfigParser.SafeConfigParser(dict(
            root=self.component_root
        ))
        config.read(os.path.join(self.__config_dir__, name + ".ini"))
        
        self.config = config
        
        # parsed = self._parseConfig(config)
        # print "parsed: "
        # print parsed
        # self.config.update(parsed)
        # 
        # if self.override_config:
        #     self.config.update(self.override_config)
        
        # print "self.config: "
        # print self.config
    
    def _parseConfig(self, config):
        items = config.items("default")
        tmp = dict()
        
        for item in items:
            tmp[item[0]] = item[1]
        
        sections = config.sections()
        for section in sections:            
            items = config.items(section)
            for item in items:
                tmp[item[0]] = item[1]
        
        return tmp
    
    def prepareRoutes(self):
        pass

class PurecodeComponentBase(ComponentBase):
    implements(IPurecodeComponent)
    
    __purecode__ = True