import _midgard
#from midgardmvc.lib.midgard import MIDGARD, init_midgard_connection
from midgardmvc.lib.midgard import init_midgard_connection

import midgardmvc.lib.utils.fixed_datetime as datetime
import midgardmvc.lib.componentloader

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
        
        #Remove trailing slash
        if len(environ.get('PATH_INFO', '')) > 1:
            environ['PATH_INFO'] = environ.get('PATH_INFO', '').rstrip('/')
        
        # if environ.has_key('paste.registry'):
        #     environ['paste.registry'].register(MIDGARD, _midgard)
        #     self.log.debug("Register MIDGARD")
        
        environ['midgard.midgard'] = _midgard
        
        timezone = self.config.get("Datetime", "timezone", "UTC")
        self.log.debug("Setting timezone to %s" % timezone)
        
        datetime.set_default_timezone(timezone)
        environ['midgard.datetime.currentTZ'] = self.getTimezone(timezone)
        environ['midgard.datetime.getTZ'] = self.getTimezone
        environ['midgard.datetime.defaultTZ'] = self.getDefaultTZ
        
        environ = midgardmvc.lib.componentloader.connect_components_to_environ(environ)
        
        return self.app(environ, start_response)

    def getTimezone(self, tz_str):
    	import pytz

    	if type(tz_str) is str or type(tz_str) is unicode:
    		return pytz.timezone(tz_str)

    	return None

    def getDefaultTZ(self):
    	return self.getTimezone(self.config.get("Datetime", "timezone", "UTC"))