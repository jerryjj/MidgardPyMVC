import logging
log = logging.getLogger(__name__)

from zope.interface import implements
from repoze.who.interfaces import IMetadataProvider
from pylons import request

from gi.repository import Midgard
from midgardmvc.lib.midgard.connection import instance as connection_instance

class MidgardAuth(object):
    """docstring for MidgardAuth"""
    
    implements(IMetadataProvider)

    def __init__(self, config):
        self.config = config
    
    #IMetadataProvider plugin
    def add_metadata(self, environ, identity):
        """Fetch Midgard person based on UUID in identity"""
        person_uuid = identity.get('repoze.who.userid')

        person = Midgard.Object.factory (connection_instance.connection, "midgard_person", person_uuid)
        #person = h.midgard.mgdschema.midgard_person(person_uuid)

        identity['midgard.person'] = person
        
def get_active_user():
    identity = request.environ.get('repoze.who.identity')
    mgd = connection_instance.connection
    if not identity:
        return None
    
    if not identity.has_key("midgard.user"):
        # if not identity.has_key("midgard.user.guid"):
        #     return h.midgard._connection.get_user()
        # else:
        st = Midgard.QueryStorage(dbclass = "midgard_user")
        qs = Midgard.QuerySelect(connection = mgd, storage = st)
        qs.toggle_read_only(False)
        qs.set_constraint(
          Midgard.QueryConstraint(
            property = Midgard.QueryProperty(property = "guid"),
            operator = "=",
            holder = Midgard.QueryValue.create_with_value(identity["midgard.user.guid"])
          )
        )
        qs.execute()
        if qs.get_results_count() == 0:
          return None

        results = qs.list_objects()
        return results[0]
       
    return identity["midgard.user"]
    
def get_active_user_person():
    identity = request.environ.get('repoze.who.identity')
    
    if not identity:
        return None
    
    return identity["midgard.person"]

def prepare_password(password, authtype):
    import hashlib
    
    if authtype.lower() == "plaintext":
        return password
    elif authtype.lower() == "sha1":
        return hashlib.sha1(password).hexdigest()
    elif authtype.lower() == "sha256":
        return hashlib.sha256(password).hexdigest()
    elif authtype.lower() == "md5":
        return hashlib.md5(password).hexdigest()
