"""Setup the midgardmvc application"""
import logging

from midgardmvc.config.environment import load_environment
from midgardmvc.lib.midgard import init_midgard_connection, init_midgard_storage

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup midgardmvc here"""
    load_environment(conf.global_conf, conf.local_conf)
    log.debug("Trying to connect to Midgard")
    
    connected = init_midgard_connection(conf["midgard.config_path"], conf["midgard.logger"])
    
    if not connected:
        return
    
    log.debug("Midgard connection successful")
    
    log.debug("Initalizing Midgard storage")
    
    initialized = init_midgard_storage(conf["midgard.config_path"], conf["midgard.logger"])
    
    if not initialized:
        return    
    
    log.debug("Midgard storage initialization done")
