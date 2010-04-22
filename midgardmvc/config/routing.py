"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper

import midgardmvc.lib.componentloader
from midgardmvc.lib.midgard.utils import controller_scan

def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'],
                 controller_scan=controller_scan)
    map.minimization = False
    
    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')
    
    map.connect('/', controller='main', action='index')
    map.connect('/{language}', controller='main', action='index', requirements=dict(language='\w{2}'))
    
    map.connect('/__mgd-auth/{action}', controller='auth')
    map.connect('/{language}/__mgd-auth/{action}', controller='auth', requirements=dict(language='\w{2}'))
    map.connect('/__mgd-auth/doLogin', controller='login', action='doLogin', conditions=dict(method=["POST"]))
    map.connect('/{language}/__mgd-auth/doLogin', controller='login', action='doLogin', requirements=dict(language='\w{2}'), conditions=dict(method=["POST"]))    
    
    # CUSTOM ROUTES HERE
    
    map = midgardmvc.lib.componentloader.connect_routes(map)
    
    map.connect('/{path}', controller="page", action="show")
    map.connect('/{language}/{path}', controller="page", action="show", requirements=dict(language='\w{2}'))
    
    map.connect('/{controller}/{action}')
    map.connect('/{controller}/{action}/{id}')
    map.connect('/{language}/{controller}/{action}', requirements=dict(language='\w{2}'))
    map.connect('/{language}/{controller}/{action}/{id}', requirements=dict(language='\w{2}'))
    
    return map
