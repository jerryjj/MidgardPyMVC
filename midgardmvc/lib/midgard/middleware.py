import _midgard
#from midgardmvc.lib.midgard import MIDGARD, init_midgard_connection
from midgardmvc.lib.midgard import init_midgard_connection

import logging

# from paste.registry import StackedObjectProxy
# MIDGARD = StackedObjectProxy(name="midgard", default=_midgard)

class MidgardMiddleware(object):
    """docstring for MidgardMiddleware"""
    def __init__(self, app, config, logger):
        self.app = app
        self.config = config
        self.logger_name = logger
        self.log = logging.getLogger(logger)
        
        self.log.debug("MidgardMiddleware::__init__")

    def __call__(self, environ, start_response):
        self.log.debug("MidgardMiddleware::__call__")
        #environ['midgard.pylons.application'] = self.app
        
        # if environ.has_key('paste.registry'):
        #     environ['paste.registry'].register(MIDGARD, _midgard)
        #     self.log.debug("Register MIDGARD")
        
        environ['midgard.midgard'] = _midgard
        
        # status = init_midgard_connection(None, self.logger_name)
        # self.log.debug("midgard connection status: %s" % status)
        
        # timezone = self.config.get("DateTime", "tz", "UTC")
        # self.log.debug("Setting timezone to %s" % timezone)
        # 
        # datetime.set_default_timezone(timezone)
        # environ['infigo.acs.datetime.currentTZ'] = self.getTimezone(timezone)
        # environ['infigo.acs.datetime.getTZ'] = self.getTimezone
        # environ['infigo.acs.datetime.defaultTZ'] = self.getDefaultTZ
        
        return self.app(environ, start_response)    