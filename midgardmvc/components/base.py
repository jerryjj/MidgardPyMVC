from midgardmvc.components.interfaces import IComponent, IPurecodeComponent
from zope.interface import implements

import ConfigParser
import os

class ComponentBase(object):
    implements(IComponent)

    __purecode__ = False
    
    __routes__ = []
    __routes_prefix__ = None
    __config_dir__ = None
    __templates_dir__ = None
    __static_files__ = None
    
    def __init__(self, config=None):
        self.override_config = config
        self.config = dict()
        self.component_root = None
        
        self.initialize()
    
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