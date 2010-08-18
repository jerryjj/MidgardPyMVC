#import _midgard
#from midgardmvc.lib.midgard import MIDGARD, init_midgard_connection
from midgardmvc.lib.midgard import init_midgard_connection

import midgardmvc.lib.utils.fixed_datetime as datetime
import midgardmvc.lib.componentloader

import logging

# from paste.registry import StackedObjectProxy
# MIDGARD = StackedObjectProxy(name="midgard", default=_midgard)

from paste.registry import StackedObjectProxy
helper_stack = StackedObjectProxy(name="helper_stack", default=dict())

class MidgardMiddleware(object):
    """docstring for MidgardMiddleware"""
    def __init__(self, app, config, logger, mgd_config_path):
        self.app = app
        self.config = config
        self.logger_name = logger
        self.log = logging.getLogger(logger)
        self.mgd_config_path = mgd_config_path
        
        self.log.debug("MidgardMiddleware::__init__")

    def __call__(self, environ, start_response):
        self.log.debug("MidgardMiddleware::__call__")
        
        init_midgard_connection(self.mgd_config_path, self.logger_name)
        
        #Remove trailing slash
        if len(environ.get('PATH_INFO', '')) > 1:
            environ['PATH_INFO'] = environ.get('PATH_INFO', '').rstrip('/')
        
        #TODO: Do language pre-checking here 
        #TODO: Implement injectors
        #http://bergie.iki.fi/blog/midcom_3_and_context_injectors/
        
        registry = environ['paste.registry']
        registry.register(helper_stack, dict())
        
        self._prepareHelperStack()
        
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

    def _prepareHelperStack(self):
        helper_stack['breadcrumb_data'] = []
        if not 'header_data' in helper_stack:
            helper_stack['header_data'] = dict(
                jquery_enabled = False,
                jquery_ui_enabled = False,
                jquery_grid_enabled = False,
                jquery_ui_enabled_version = None,
                jquery_ui_loaded_parts = [],
                jquery_inits = "",            
                element_groups = [],
                active_element_group = None,
                prev_element_group = None,
                head_datas = dict(
                    prepend_script = {},
                    js = {},
                    script = {},
                    jquery_states = {},
                    link = {},
                    meta = {}
                ),
                js_head_urls = [],
                link_head_urls = []
            )