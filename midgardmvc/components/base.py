from midgardmvc.components.interfaces import IComponent, IPurecodeComponent
from zope.interface import implements

class ComponentBase(object):
    implements(IComponent)

    __purecode__ = False
    
    __routes__ = []
    __routes_prefix__ = None
    __templates_dir__ = None
    
    def __init__(self, config=None):
        self.config = config
        
        self.initialize()

    def prepareRoutes(self):
        pass

class PurecodeComponentBase(ComponentBase):
    implements(IPurecodeComponent)
    
    __purecode__ = True