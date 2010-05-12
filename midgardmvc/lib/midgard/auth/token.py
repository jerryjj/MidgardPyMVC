import hashlib

from zope.interface import implements
from repoze.who.interfaces import IIdentifier, IAuthenticator

from pylons import config

import logging
log = logging.getLogger(__name__)

from midgardmvc.lib.midgard.auth import MidgardAuth
import midgardmvc.lib.helpers as h

import datetime
from codecs import utf_8_decode
from codecs import utf_8_encode
import time

#from webob import Request
from webob.exc import HTTPFound

from paste.auth import auth_tkt
from paste.request import construct_url, get_cookies

_NOW_TESTING = None  # unit tests can replace
def _now():  #pragma NO COVERAGE
    if _NOW_TESTING is not None:
        return _NOW_TESTING
    return datetime.datetime.now()

class MidgardTokenAuth(MidgardAuth):
    implements(IIdentifier, IAuthenticator)
    
    userid_type_decoders = {
        'int':int,
        'unicode':lambda x: utf_8_decode(x)[0],
        }

    userid_type_encoders = {
        int: ('int', str),
        long: ('int', str),
        unicode: ('unicode', lambda x: utf_8_encode(x)[0]),
        }
    
    def __init__(self, config):
        self.config = dict(
            cookie_name="midgard.auth.tokenauth",
            secure=True,
            include_ip=True,
            timeout=None,
            reissue_time=None
        )        
        self.config.update(config)
        
        self.authtype = "Plaintext"

    # IIdentifier
    def identify(self, environ):
        log.debug("tokenAuth identify")
        cookies = get_cookies(environ)
        cookie = cookies.get(self.config["cookie_name"])
        
        if cookie is None or not cookie.value:
            return self._create_tokenUser(environ)
        
        if self.config["include_ip"]:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'

        try:
            timestamp, userid, tokens, user_data = auth_tkt.parse_ticket(
                self.config["secret"], cookie.value, remote_addr)
        except auth_tkt.BadTicket:
            return self._create_tokenUser(environ)

        if self.config["timeout"] and ( (timestamp + self.config["timeout"]) < time.time() ):
            return self._create_tokenUser(environ)

        userid_typename = 'userid_type:'
        user_data_info = user_data.split('|')
        for datum in filter(None, user_data_info):
            if datum.startswith(userid_typename):
                userid_type = datum[len(userid_typename):]
                decoder = self.userid_type_decoders.get(userid_type)
                if decoder:
                    userid = decoder(userid)

        environ['REMOTE_USER_TOKENS'] = tokens
        environ['REMOTE_USER_DATA'] = user_data
        environ['AUTH_TYPE'] = 'cookie'
        
        user_guid, login = userid.split("|")
        
        identity = {}
        identity['timestamp'] = timestamp
        identity['midgard.user.guid'] = user_guid
        identity['login'] = login
        identity['tokens'] = tokens
        identity['userdata'] = user_data

        return identity

    # IIdentifier
    def remember(self, environ, identity):
        log.debug("tokenAuth remember")
        
        if self.config["include_ip"]:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'

        cookies = get_cookies(environ)
        old_cookie = cookies.get(self.config["cookie_name"])
        existing = cookies.get(self.config["cookie_name"])
        old_cookie_value = getattr(existing, 'value', None)
        max_age = identity.get('max_age', None)

        timestamp, userid, tokens, userdata = None, '', '', ''

        if old_cookie_value:
            try:
                timestamp,userid,tokens,userdata = auth_tkt.parse_ticket(
                    self.config["secret"], old_cookie_value, remote_addr)
            except auth_tkt.BadTicket:
                log.error("Bad ticket")
                pass

        who_userid = identity['midgard.user.guid'] + "|" + identity.get('login')
        who_tokens = identity.get('tokens', '')
        who_userdata = identity.get('userdata', '')

        encoding_data = self.userid_type_encoders.get(type(who_userid))
        if encoding_data:
            encoding, encoder = encoding_data
            who_userid = encoder(who_userid)
            who_userdata = 'userid_type:%s' % encoding

        if not isinstance(tokens, basestring):
            tokens = ','.join(tokens)
        if not isinstance(who_tokens, basestring):
            who_tokens = ','.join(who_tokens)
        old_data = (userid, tokens, userdata)
        new_data = (who_userid, who_tokens, who_userdata)

        if old_data != new_data or (self.config["reissue_time"] and
                ( (timestamp + self.config["reissue_time"]) < time.time() )):
            ticket = auth_tkt.AuthTicket(
                self.config["secret"],
                who_userid,
                remote_addr,
                tokens=who_tokens,
                user_data=who_userdata,
                cookie_name=self.config["cookie_name"],
                secure=self.config["secure"])
            new_cookie_value = ticket.cookie_value()

            cur_domain = environ.get('HTTP_HOST', environ.get('SERVER_NAME'))
            wild_domain = '.' + cur_domain
            if old_cookie_value != new_cookie_value:
                if "auth_remember_allow" in environ and environ["auth_remember_allow"] == False:
                    return None
                
                # return a set of Set-Cookie headers
                return self._get_cookies(environ, new_cookie_value, max_age)

    # IIdentifier
    def forget(self, environ, identity):
        log.debug("tokenAuth forget")
        return self._get_cookies(environ, 'INVALID', 0)

    # IAuthenticator
    def authenticate(self, environ, identity):
        log.debug("tokenAuth authenticate")
        log.debug(identity)
        
        user_guid = identity.get('midgard.user.guid')        
        
        if user_guid is None:
            return None
        
        if "midgard.midgard" in environ:
            midgard = environ["midgard.midgard"]
        else:
            midgard = h.midgard
        
        user = midgard.db.user.get({"login": identity.get("login"), "password": identity.get("login"), "authtype": self.authtype}) #, "password": password
        
        # qb = midgard.query_builder('midgard_user')
        # qb.add_constraint('guid', '=', user_guid)
        # 
        # user = False
        # results = qb.execute()
        # if len(results) > 0:
        #     user = results[0]
        
        log.debug("user: ")
        log.debug(user)

        if not user:
            log.error("User %s (%s / %s) not found, reason: %s" % (user_guid, identity.get("login"), self.authtype, midgard._connection.get_error_string()))
            return None
        
        status = user.log_in()
        log.debug("User login status: %s" % status)
        
        if not status:
            return None
        
        identity["midgard.user"] = user
        if not identity.get("midgard.person.guid"):
            person = user.get_person()
            log.debug("person: ")
            log.debug(person)
            
            identity["midgard.person.guid"] = person.guid
        
        return identity["midgard.person.guid"]
    
    def _create_tokenUser(self, environ):
        log.debug("tokenAuth _create_tokenUser")
        
        if "midgard.midgard" in environ:
            midgard = environ["midgard.midgard"]
        else:
            midgard = h.midgard
        
        person = midgard.mgdschema.midgard_person()
        person.firstname = "TokenAuth"
        person.lastname = "Person"
        
        try:
            status = person.create()
            log.debug("Person created with GUID: %s" % person.guid)
        except:
            log.error("Could not create person, reason: %s" % (midgard._connection.get_error_string()))
            return None
        
        if not status:
            log.error("Could not create person, reason: %s" % (midgard._connection.get_error_string()))
            return None
        
        #user_login_name = "tokenauth_%s_%s" % (int(time.time()), person.guid)
        user_login_name = "tokenauth_%s" % (person.guid)
        
        user = midgard.db.user()
        user.login = user_login_name
        user.password = user_login_name
        user.authtype = self.authtype
        user.active = True
        user.usertype = 1
        
        try:
            status = user.create()
            log.debug("User %s created with GUID: %s" % (user.login, user.guid))
        except:
            log.error("Could not create user, reason: %s" % (midgard._connection.get_error_string()))
            return None
        
        if not status:
            log.error("Could not create user, reason: %s" % (midgard._connection.get_error_string()))
            return None
        
        person_status = user.set_person(person)
        log.debug("set person status %s" % person_status)
        
        identity = {
            "login": user_login_name,
            "midgard.user.guid": user.guid,
            "midgard.person.guid": person.guid
        }
        
        return identity
    
    def _get_cookies(self, environ, value, max_age=None):
        if max_age is not None:
            later = _now() + datetime.timedelta(seconds=int(max_age))
            # Wdy, DD-Mon-YY HH:MM:SS GMT
            expires = later.strftime('%a, %d %b %Y %H:%M:%S')
            # the Expires header is *required* at least for IE7 (IE7 does
            # not respect Max-Age)
            max_age = "; Max-Age=%s; Expires=%s" % (max_age, expires)
        else:
            max_age = ''

        cur_domain = environ.get('HTTP_HOST', environ.get('SERVER_NAME'))
        wild_domain = '.' + cur_domain
        
        cookies = [
            ('Set-Cookie', '%s="%s"; Path=/%s' % (
            self.config["cookie_name"], value, max_age)),
            ('Set-Cookie', '%s="%s"; Path=/; Domain=%s%s' % (
            self.config["cookie_name"], value, cur_domain, max_age)),
            ('Set-Cookie', '%s="%s"; Path=/; Domain=%s%s' % (
            self.config["cookie_name"], value, wild_domain, max_age))
            ]
        
        return cookies

def make_plugin(**config):
    if not config.has_key("secret") or not config["secret"]:
        raise ValueError("'secret' must not be None.")
    
    if config.has_key("timeout"):
        config["timeout"] = int(config["timeout"])
    if config.has_key("reissue_time"):
        config["reissue_time"] = int(config["reissue_time"])

    if config.has_key("timeout") and ( (not config.has_key("reissue_time")) or (config["reissue_time"] > config["timeout"]) ):
        raise ValueError('When timeout is specified, reissue_time must '
                         'be set to a lower value')
        
    return MidgardTokenAuth(config)
