from zope.interface import Interface

class IComponent(Interface):
    """ Component interface
    """

    def __init__(self, config=None):
        """ Init
        """
    
    def initialize(self):
        """ Initialize component. This will be called from __init__
        """

    def prepareRoutes(self):
        """ Prepare routes
        """
    
class IPurecodeComponent(IComponent):
    """ Purecode component interface
    """