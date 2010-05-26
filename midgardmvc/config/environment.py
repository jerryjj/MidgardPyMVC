"""Pylons environment configuration"""
import os

from mako.lookup import TemplateLookup
from pylons import config
from pylons.error import handle_mako_error

import midgardmvc.lib.app_globals as app_globals
import midgardmvc.lib.helpers
from midgardmvc.config.routing import make_map

import midgardmvc.lib.componentloader
from paste.deploy.converters import asbool

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))    
    paths = dict(root=root,
                 controllers=[os.path.join(root, 'controllers')],
                 static_files=[os.path.join(root, 'public')],
                 templates=[os.path.join(root, 'templates')])
    
    midgardmvc.lib.componentloader.load_all(global_conf)
    paths = midgardmvc.lib.componentloader.update_paths(paths)
    
    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='midgardmvc', paths=paths)
    
    if global_conf.has_key("mail.on") and asbool(global_conf["mail.on"]):
        from turbomail.adapters import tm_pylons
        tm_pylons.config = config
        tm_pylons.start_extension()
    
    config['routes.map'] = make_map()
    config['pylons.app_globals'] = app_globals.Globals(config)
    config['pylons.h'] = midgardmvc.lib.helpers

    # Setup cache object as early as possible
    import pylons
    pylons.cache._push_object(config['pylons.app_globals'].cache)

    # Create the Mako TemplateLookup, with the default auto-escaping
    config['pylons.app_globals'].mako_lookup = TemplateLookup(
        directories=paths['templates'],
        error_handler=handle_mako_error,
        module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
        input_encoding='utf-8', default_filters=['escape'],
        imports=['from webhelpers.html import escape'],
        filesystem_checks=config['debug'])

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    
    return config
