import hashlib

from zope.interface import implements
from repoze.who.interfaces import IAuthenticator

from pylons import config

import logging
log = logging.getLogger(__name__)

from midgardmvc.lib.midgard.auth import MidgardAuth, prepare_password

from gi.repository import Midgard, GObject
from midgardmvc.lib.midgard.connection import instance as connection_instance

def midgard_user_get(username, authtype, password):
  mgd = connection_instance.connection
  strg = Midgard.QueryStorage(dbclass = "MidgardUser")
  qs = Midgard.QuerySelect(connection = mgd, storage = strg)
  qs.toggle_read_only(False)
  group = Midgard.QueryConstraintGroup(grouptype = "AND")
  constraint_login = Midgard.QueryConstraint(
    property = Midgard.QueryProperty(property = "login"),
    operator = "=",
    holder = Midgard.QueryValue.create_with_value(str(username))
  )
  group.add_constraint(constraint_login)

  constraint_authtype = Midgard.QueryConstraint(
    property = Midgard.QueryProperty(property = "authtype"),
    operator = "=",
    holder = Midgard.QueryValue.create_with_value(str(authtype))
  )
  group.add_constraint(constraint_authtype)

  if password is not None:
    constraint_pwd = Midgard.QueryConstraint(
      property = Midgard.QueryProperty(property = "password"),
      operator = "=",
      holder = Midgard.QueryValue.create_with_value(str(password))
    )
    group.add_constraint(constraint_pwd)
  
  qs.set_constraint(group)

  try:
    qs.execute()
  except GObject.GError as e:
    log.debug("Can not fetch user. Query execution failed")
    return None
  
  if qs.get_results_count() == 0:
    return None
  
  objects = qs.list_objects()
  return objects[0]

class MidgardPasswordAuth(MidgardAuth):
    implements(IAuthenticator)
        
    #IAuthenticator plugin
    def authenticate(self, environ, identity):
        authtype = self.config["authtype"]
        mgd = connection_instance.connection
        
        try:
            username = identity['login']
            password = prepare_password(identity['password'], authtype)
        except KeyError:
            return None
        
        log.debug("authenticate user with %s / %s using authtype: %s" % (username, password, authtype))

        user = midgard_user_get(username, authtype, password)
        #user = Midgard.User.get(connection_instance.connection, {"login": username, "authtype": authtype, "password": password})
        
        log.debug("User:")
        log.debug(user)
        
        if not user:
            return None
        
        status = user.log_in()
        
        log.debug("login status %s:" % status)
        
        if not status:
            return None
        
        person = user.get_person()
       
        print user.get_property ("person")
        log.debug("Person:")
        log.debug(person)
        
        identity["midgard.user"] = user
        identity["midgard.user.guid"] = user.get_property("guid")
        identity["midgard.person.guid"] = person.get_property("guid")
        
        return person.get_property("guid")

def make_plugin(**config):
    return MidgardPasswordAuth(config)
