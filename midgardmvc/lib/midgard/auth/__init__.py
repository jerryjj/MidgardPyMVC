import logging
log = logging.getLogger(__name__)

from zope.interface import implements
from repoze.who.interfaces import IMetadataProvider
from pylons import request

import midgardmvc.lib.helpers as h

class MidgardAuth(object):
    """docstring for MidgardAuth"""
    
    implements(IMetadataProvider)

    def __init__(self, config):
        self.config = config
    
    #IMetadataProvider plugin
    def add_metadata(self, environ, identity):
        """Fetch Midgard person based on UUID in identity"""
        person_uuid = identity.get('repoze.who.userid')

        person = h.midgard.mgdschema.midgard_person(person_uuid)

        identity['midgard.person'] = person
        
def get_active_user():
    identity = request.environ.get('repoze.who.identity')
    
    if not identity:
        return None
    
    if not identity.has_key("midgard.user"):
        # if not identity.has_key("midgard.user.guid"):
        #     return h.midgard._connection.get_user()
        # else:
        qb = h.midgard.query_builder('midgard_user')
        qb.add_constraint('guid', '=', identity["midgard.user.guid"])
        
        results = qb.execute()
        if len(results) > 0:
            return results[0]
        
        return None
    
    return identity["midgard.user"]
    
def get_active_user_person():
    identity = request.environ.get('repoze.who.identity')
    
    if not identity:
        return None
    
    return identity["midgard.person"]