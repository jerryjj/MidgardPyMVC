"""Pylons middleware initialization"""
from beaker.middleware import CacheMiddleware, SessionMiddleware
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from pylons import config
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware

from midgardmvc.config.environment import load_environment
from midgardmvc.lib.midgard import make_midgard_middleware, init_midgard_connection, init_midgard_authentication

from cogen.web.async import LazyStartResponseMiddleware
from cogen.web.async import SynchronousInputMiddleware

def make_app(global_conf, full_stack=True, static_files=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether this application provides a full WSGI stack (by default,
        meaning it handles its own exceptions and errors). Disable
        full_stack when this application is "managed" by another WSGI
        middleware.

    ``static_files``
        Whether this application serves its own static files; disable
        when another web server is responsible for serving them.

    ``app_conf``
        The application's local configuration. Normally specified in
        the [app:<name>] section of the Paste ini file (where <name>
        defaults to main).

    """
    # Configure the Pylons environment
    load_environment(global_conf, app_conf)
    
    init_midgard_connection(config["midgard.config_path"], config["midgard.logger"])
    
    # The Pylons WSGI app
    app = PylonsApp()

    # Routing/Session/Cache Middleware
    app = RoutesMiddleware(app, config['routes.map'])
    app = CacheMiddleware(app, config)
    
    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)
    
    if asbool(full_stack):
        # Handle Python exceptions
        #app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        if asbool(config['debug']):
            app = StatusCodeRedirect(app)
        else:
            app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])

    # Establish the Registry for this application
    app = RegistryManager(app, streaming=True) #, streaming=True

    if asbool(static_files):
        # Serve static files
        static_apps = []
        if type(config['pylons.paths']['static_files']) == list:
            for static_path in config['pylons.paths']['static_files']:
                static_apps.append(StaticURLParser(static_path))
        else:
            static_apps.append(StaticURLParser(config['pylons.paths']['static_files']))
        
        static_apps.append(app)
        app = Cascade(static_apps)
    
    app = init_midgard_authentication(app, global_conf, app_conf)

    app = make_midgard_middleware(app, config["midgard.config_path"], config["midgard.logger"])
    
    app = LazyStartResponseMiddleware(app, global_conf)    
    app = SessionMiddleware(app, config)    
    app = SynchronousInputMiddleware(app, global_conf)

    return app
