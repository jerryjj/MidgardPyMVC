import os
import _midgard as midgard

from midgardmvc.lib.midgard.connection import instance as connection_instance

class StorageWrapper(object):
    """docstring for StorageWrapper"""
    
    def __init__(self):
        self._log = None
        self.config = dict(
            schemas = []
        )
        self._connection_config = dict()
        
        self._initialized = False

    @property
    def initialized(self):
        return self._initialized
    
    def setLogger(self, logger):
        self._log = logger

    def setConfig(self, config):
        self.config.update(config)
        
        self.config["schemas"] = self.config["schemas"].split(";")
        
    def initialize(self):
        self._initialized = True
        
        self.createBaseStorage()
        self.createClassStorages()
        
        if self.config["create_default_content"]:
            self.createDefaultContent()
        
    def baseStorageExists(self):
        # if connection_instance.midgard_config.dbtype.lower() == "sqlite":
        #     """TODO: Try to resolve using dbdir -configuration key, after it is enbaled in Midgard"""
        #     db_file_path = os.path.expanduser('~/.midgard2/data/' + connection_instance.midgard_config.database + '.db')
        #     return os.path.exists(db_file_path)
        
        return midgard.storage.class_storage_exists("midgard_user")
    
    def classStorageExists(self, classname):
        return midgard.storage.class_storage_exists(classname)
    
    def createBaseStorage(self):
        if self.baseStorageExists():
            self._log.debug("Base storage already exists")
            return False

        import threading

        create_ok = True
        cthread = threading.Thread(name='base storage', target=_returnToPointer, args=(midgard.storage.create_base_storage, create_ok))
        if cthread == None:
            self._log.error("could not create thread for create_base_storage()")
            raise Exception("could not create thread for create_base_storage()")
        cthread.start()
        while cthread.isAlive():
            self._log.debug("waiting for %s" % cthread.getName())
            cthread.join(0.1)
        self._log.debug("waiting (blocking) for %s" % cthread.getName())
        cthread.join()
        self._log.debug("done")
        if not create_ok:
            self._log.error("Could not create base storage, reason: %s" % midgard._connection.get_error_string())
            raise Exception("Could not create base storage, reason: %s" % midgard._connection.get_error_string())
    
    def createClassStorages(self):
        import threading
        
        for classname in self.config["schemas"]:
            create_ok = True
            update_ok = True
            
            if not self.classStorageExists(classname):
                self._log.debug("creating class storage for %s" % classname)
                cthread = threading.Thread(name=classname + ' storage', target=_returnToPointer, args=(midgard.storage.create_class_storage, create_ok), kwargs={ 'function_args': classname, } )
                if cthread == None:
                    self._log.error("could not create thread for create_class_storage(%s)" % classname)
                    raise Exception("could not create thread for create_class_storage(%s)" % classname)
                cthread.start()
                while cthread.isAlive():
                    self._log.debug("waiting for %s" % cthread.getName())
                    cthread.join(0.1)
                self._log.debug("waiting (blocking) for %s" % cthread.getName())
                cthread.join()
                self._log.debug("done")
            else:
                self._log.debug("Class %s exists" % classname)
                self._log.debug("Trying to update...")
                
                cthread = threading.Thread(name=classname + ' storageUpdate', target=_returnToPointer, args=(midgard.storage.update_class_storage, update_ok), kwargs={ 'function_args': classname, } )
                if cthread == None:
                    self._log.error("could not create thread for update_class_storage(%s)" % classname)
                    raise Exception("could not create thread for update_class_storage(%s)" % classname)
                cthread.start()
                while cthread.isAlive():
                    self._log.debug("waiting for %s" % cthread.getName())
                    cthread.join(0.1)
                self._log.debug("waiting (blocking) for %s" % cthread.getName())
                cthread.join()
                self._log.debug("done")
                
                if not update_ok:
                    self._log.error("Error while updating storage for class %s, reason: %s" % (classname, midgard._connection.get_error_string()))
                
            if not create_ok:
                self._log.error("Could not create storage for class %s, reason: %s" % (classname, midgard._connection.get_error_string()))
                raise Exception("Could not create storage for class %s, reason: %s" % (classname, midgard._connection.get_error_string()))
    
    def createDefaultContent(self):
        """Creates some default content for basic Midgard site"""
        
        #Create root page
        root_page = midgard.mgdschema.midgard_page()
        root_page_exists = root_page.get_by_path('/midcom_root')
        
        if not root_page_exists:
            self._log.debug("/midcom_root -page not found. Creating...")
            root_page.name = "midcom_root"
            root_page.title = "Midcom root"
            root_page.content = "Hello, world!"
            
            try:
                root_page.create()
                self._log.debug("/midcom_root -page created")
            except:
                self._log.error("Could not create root page, reason: %s" % midgard._connection.get_error_string())
    
def _returnToPointer(function_pointer, return_pointer, function_args=None):
    if function_args is None:
        return_pointer = function_pointer()
        return
    return_pointer = function_pointer(function_args)

instance = StorageWrapper()