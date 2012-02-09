import os
import gobject
from gi.repository import Midgard, GObject

from midgardmvc.lib.midgard.connection import instance as connection_instance
from midgardmvc.lib.midgard.utils import asBool

def get_dbobject_derived(typename, types):
  children = GObject.type_children(typename)
  for gtype in children:
    childname = GObject.type_name(gtype)
    get_dbobject_derived(childname, types)
    # FIXME, core should support some routines to check if type could have storage 
    if (GObject.type_is_a(gtype, GObject.type_from_name("MidgardBaseInterface"))
        or gtype.is_abstract()
        or childname == "MidgardMetadata"):
      continue
    types.append(childname)

_available_classes = []
def get_mgdschema_classes(force_reload = False):
    global _available_classes
    
    if len(_available_classes) > 0 and not force_reload:
        return _available_classes
   
    get_dbobject_derived("MidgardDBObject", _available_classes)

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
        
        if (isinstance(self.config["schemas"], str)):
            self.config["schemas"] = self.config["schemas"].split(";")
        
        if not self.config["schemas"]:
            self.config["schemas"] = get_mgdschema_classes()
        
    def initialize(self):
        self._initialized = True
        
        self.createBaseStorage()
        self.createClassStorages()
        
        if asBool(self.config["create_default_content"]):
            self.createDefaultContent()
        
        return False
    
    def classStorageExists(self, classname):
        try:
            return midgard.storage.class_storage_exists(classname)
        except Exception, e:
            self._log.error("Exception while calling midgard.storage.class_storage_exists(%s): %s" % (classname, e))
        return False
    
    def createBaseStorage(self):        
        self._log.debug("Creating base storage")
        
        create_ok = midgard.storage.create_base_storage()
        
        if not create_ok:
            self._log.error("Could not create base storage, reason: %s" % midgard._connection.get_error_string())
            raise Exception("Could not create base storage, reason: %s" % midgard._connection.get_error_string())
    
    def createClassStorages(self):        
        for classname in self.config["schemas"]:
            create_ok = True
            update_ok = True
            
            if not self.classStorageExists(classname):
                self._log.debug("creating class storage for %s" % classname)
                create_ok = midgard.storage.create_class_storage(classname)
            else:
                self._log.debug("Class %s exists" % classname)
                self._log.debug("Trying to update...")
                
                update_ok = midgard.storage.update_class_storage(classname)
                
                if not update_ok:
                    self._log.error("Error while updating storage for class %s, reason: %s" % (classname, midgard._connection.get_error_string()))
                
            if not create_ok:
                self._log.error("Could not create storage for class %s, reason: %s" % (classname, midgard._connection.get_error_string()))
                raise Exception("Could not create storage for class %s, reason: %s" % (classname, midgard._connection.get_error_string()))
    
    def createDefaultContent(self):
        """Creates some default content for basic Midgard site"""
        
        #Create root node
        root_node = midgard.mgdschema.midgardmvc_core_node()
        
        if not root_node.get_by_path('/midcom_root'):
            self._log.debug("/midcom_root -node not found. Creating...")
            root_node.name = "midcom_root"
            root_node.title = "Midcom root"
            root_node.content = "Hello, world!"
            
            try:
                root_node.create()
                self._log.debug("/midcom_root -node created")
            except:
                self._log.error("Could not create root node, reason: %s" % midgard._connection.get_error_string())
        
def _returnToPointer(function_pointer, return_pointer, function_args=None):
    if function_args is None:
        return_pointer = function_pointer()
        return
    return_pointer = function_pointer(function_args)

instance = StorageWrapper()
