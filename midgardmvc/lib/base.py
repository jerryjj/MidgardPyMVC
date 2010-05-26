"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render
from pylons import request, tmpl_context as c
from pylons.i18n.translation import _, set_lang

import midgardmvc.lib.helpers as h

class BaseController(WSGIController):
    def __before__(self, language="en"):
        c.title = _("Midgard CMS")
        
        h.header.addMeta(name="generator", value="MidgardPyMVC")
        
        if language:
            set_lang(language)

        c.language = language
    
    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        return WSGIController.__call__(self, environ, start_response)
