import hashlib

from zope.interface import implements
from repoze.who.interfaces import IAuthenticator

from pylons import config

import logging
log = logging.getLogger(__name__)

from midgardmvc.lib.midgard.auth import MidgardAuth, prepare_password
import midgardmvc.lib.helpers as h

class MidgardPasswordAuth(MidgardAuth):
    implements(IAuthenticator)
        
    #IAuthenticator plugin
    def authenticate(self, environ, identity):
        authtype = self.config["authtype"]
        
        try:
            username = identity['login']
            password = prepare_password(identity['password'], authtype)
        except KeyError:
            return None
        
        log.debug("authenticate user with %s / %s using authtype: %s" % (username, password, authtype))

        user = h.midgard.db.user.get({"login": username, "authtype": authtype, "password": password})
        
        log.debug("User:")
        log.debug(user)
        
        if not user:
            return None
        
        status = user.log_in()
        
        log.debug("login status %s:" % status)
        
        if not status:
            return None
        
        person = user.get_person()
        
        log.debug("Person:")
        log.debug(person)
        
        identity["midgard.user"] = user
        identity["midgard.user.guid"] = user.guid
        identity["midgard.person.guid"] = person.guid
        
        return person.guid

def make_plugin(**config):
    return MidgardPasswordAuth(config)
