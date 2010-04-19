import os
import logging
import ConfigParser

import _midgard as midgard

log = None

configuration = midgard.config()
database_path = None
connection = None
connected = False

def initMidgard(app_config, mgd_config_path, mgd_logger):
    global log    
    log = logging.getLogger(mgd_logger)
    
    config = ConfigParser.SafeConfigParser(defaults={
        "dbtype": "SQLite",
        "database": "midgardmvc"
    })
    config.read(mgd_config_path)
    
    mgd_config = config.items("Configuration")
    used_classes = config.get("Configuration", "schemas").split(";")
    
    log.debug("Schemas in use: %s" % used_classes)
    
    configure(app_config, mgd_config)
    connect()
    initializeDB(used_classes)

def configure(app_config, mgd_config):
    global configuration, connection, database_path
    
    allowed_keys = ["dbtype", "dbuser", "dbpass", "dbport", "database", "blobdir", "loglevel"] #dbdir
    
    log.debug("Configuring Midgard with config: %s" % mgd_config)
    
    db_path = None
    
    for item in mgd_config:
        log.debug("key: %s => %s" % (item[0], item[1]))
        if not item[0] in allowed_keys:
            if item[0] == "db_path":
                db_path = item[1]
            continue
        setattr(configuration, item[0], item[1])
        
    database_path = os.path.expanduser('~/.midgard2/data/' + configuration.database + '.db')
    # database_path = database_path = os.path.join(app_config["cache_dir"], configuration.database + '.db')
    # if db_path:
    #     database_path = os.path.join(db_path, configuration.database + '.db')
    
    #log.debug("database_path: %s" % database_path) 
    
    connection = midgard.connection()

def databaseExists():
    return os.path.exists(database_path)

def connect():
    """Open connection to database or raise exception on failure"""
    global connection, connected
    
    if connected:
        return
    
    connected = connection.open_config(configuration)
    
    if not connected:
        raise Exception('Could not open database connection, reason: %s' % midgard._connection.get_error_string())

def initializeDB(classes):
    if databaseExists():
        log.debug("database path already exists")
        return
    
    import threading
    
    create_ok = True
    cthread = threading.Thread(name='base storage', target=_returnToPointer, args=(midgard.storage.create_base_storage, create_ok))
    if cthread == None:
        raise Exception("could not create thread for create_base_storage()")
    cthread.start()
    while cthread.isAlive():
        log.debug("waiting for %s" % cthread.getName())
        cthread.join(0.1)
    log.debug("waiting (blocking) for %s" % cthread.getName())
    cthread.join()
    log.debug("done")
    if not create_ok:
        raise Exception('Could not create base storage, reason: %s' % midgard._connection.get_error_string())
    for classname in classes:
        create_ok = True
        cthread = threading.Thread(name=classname + ' storage', target=_returnToPointer, args=(midgard.storage.create_class_storage, create_ok), kwargs={ 'function_args': classname, } )
        if cthread == None:
            raise Exception("could not create thread for create_class_storage(%s)" % classname)
        cthread.start()
        while cthread.isAlive():
            log.debug("waiting for %s" % cthread.getName())
            cthread.join(0.1)
        log.debug("waiting (blocking) for %s" % cthread.getName())
        cthread.join()
        log.debug("done")
        if not create_ok:
            raise Exception('Could not create storage for class' + classname + ', reason: %s' % midgard._connection.get_error_string())

def _returnToPointer(function_pointer, return_pointer, function_args=None):
    if function_args is None:
        return_pointer = function_pointer()
        return
    return_pointer = function_pointer(function_args)