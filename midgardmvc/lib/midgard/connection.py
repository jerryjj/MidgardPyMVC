import os
import _midgard as midgard

class NoOpenConnections(Exception): pass

class ConnectionWrapper(object):
    """docstring for ConnectionWrapper"""
    
    allowed_mgd_config_keys = ["dbtype", "dbuser", "dbpass", "dbport", "database", "dbdir", "blobdir", "loglevel"]
    
    def __init__(self):
        self._log = None
        self.config = dict(
            dbtype = "SQLite",
            database = "midgardmvc",
            sitegroup = None,
        )
        
        self._connected = False
        
        self._mgd_config = midgard.config()
        self._connection = midgard.connection()
    
    @property
    def connected(self):
        return self._connected
    
    @property
    def connection(self):
        if not self._connected:
            raise NoOpenConnections("Midgard connection not yet initialized!")
        
        return self._connection
    
    @property
    def midgard_config(self):
        """Property for Midgard config object"""
        return self._mgd_config
    
    def setLogger(self, logger):
        self._log = logger
        
    def setConfig(self, config):
        self.config.update(config)
        
        for key, value in self.config.iteritems():
            if not key in ConnectionWrapper.allowed_mgd_config_keys:
                continue
            
            setattr(self._mgd_config, key, value)
        
        # if configuration.has_key("dbdir")        
        #self.database_path = os.path.expanduser('~/.midgard2/data/' + self._mgd_config.database + '.db')
        
    def connect(self):
        if self._connected:
            return True
        
        self._connected = self._connection.open_config(self._mgd_config)
        
        if not self._connected:
            raise Exception('Could not open database connection, reason: %s' % midgard._connection.get_error_string())
        
        # if self.config["sitegroup"]:
        #     self._log.debug("Trying to set sitegroup to %s" % self.config["sitegroup"])
        #     if not self._connection.set_sitegroup(self.config["sitegroup"]):
        #         self._log.error("Sitegroup %s not found" % self.config["sitegroup"])
        
        return True

instance = ConnectionWrapper()
        