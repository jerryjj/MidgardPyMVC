import logging
import ConfigParser

from pylons import config
from paste.deploy.converters import asbool

from midgardmvc.lib.midgard.connection import instance as connection_instance
from midgardmvc.lib.midgard.storage import instance as storage_instance

_mgd_config = None

def init_midgard_connection(mgd_config_path, mgd_logger):    
    global _mgd_config
    
    _mgd_config = ConfigParser.SafeConfigParser()
    _mgd_config.read(mgd_config_path)
    
    parse_midgard_config_to_globals(_mgd_config)
    
    if not connection_instance.connected:    
        connection_config = get_section_from_config(_mgd_config, "Connection")
    
        connection_instance.setLogger(logging.getLogger(mgd_logger))
        connection_instance.setConfig(connection_config)

        connection_instance.connect()
    
    return connection_instance.connected
    
def init_midgard_storage(mgd_config_path, mgd_logger):    
    mgd_config = ConfigParser.SafeConfigParser()
    mgd_config.read(mgd_config_path)

    if not storage_instance.initialized:
        storage_config = get_section_from_config(mgd_config, "Storage")
        
        storage_instance.setLogger(logging.getLogger(mgd_logger))
        storage_instance.setConfig(storage_config)
    
        storage_instance.initialize()

    return storage_instance.initialized

def init_midgard_authentication(app, global_conf, app_conf):
    if config["midgard.authentication.enabled"]:
        from repoze.who.config import make_middleware_with_config
        
        app = make_middleware_with_config(app, global_conf, config['who.config_file'], config['who.log_file'], config['who.log_level'])
    
    return app

def parse_midgard_config_to_globals(midgard_config):    
    def _resolve_key(section, key):
        return "midgard.%s.%s" % (section, key)
    
    config[_resolve_key("authentication", "enabled")] = asbool(_mgd_config.get("Authentication", "enabled", False))
    
    connection_config = get_section_from_config(_mgd_config, "Connection")
    for k, v in connection_config.iteritems():
        config[_resolve_key("connection", k)] = v
    
def get_section_from_config(config, section):
    items = config.items(section)
    tmp = dict()
    
    for item in items:
        tmp[item[0]] = item[1]
    
    return tmp

def get_connection():
    return connection_instance.connection