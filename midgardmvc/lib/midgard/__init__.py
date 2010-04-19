import logging
import ConfigParser

from midgardmvc.lib.midgard.connection import instance as connection_instance
from midgardmvc.lib.midgard.storage import instance as storage_instance

def init_midgard_connection(mgd_config_path, mgd_logger, pylons_config):    
    config = ConfigParser.SafeConfigParser()
    config.read(mgd_config_path)
    
    if not connection_instance.connected:    
        connection_config = get_section_from_config(config, "Connection")
    
        connection_instance.setLogger(logging.getLogger(mgd_logger))
        connection_instance.setConfig(connection_config)

        connection_instance.connect()
    
    return connection_instance.connected
    
def init_midgard_storage(mgd_config_path, mgd_logger, pylons_config):    
    config = ConfigParser.SafeConfigParser()
    config.read(mgd_config_path)

    if not storage_instance.initialized:
        storage_config = get_section_from_config(config, "Storage")
        
        storage_instance.setLogger(logging.getLogger(mgd_logger))
        storage_instance.setConfig(storage_config)
    
        storage_instance.initialize()

    return storage_instance.initialized

def get_section_from_config(config, section):
    items = config.items(section)
    tmp = dict()
    
    for item in items:
        tmp[item[0]] = item[1]
    
    return tmp

def get_connection():
    return connection_instance.connection