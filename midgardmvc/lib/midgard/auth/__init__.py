import logging
log = logging.getLogger(__name__)

from zope.interface import implements
from repoze.who.interfaces import IMetadataProvider

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

        log.debug("metadata Person:")
        log.debug(person)

        identity['midgard_person'] = person
        
    