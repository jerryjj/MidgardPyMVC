import datetime
from codecs import utf_8_decode
from codecs import utf_8_encode
import os
import time

import logging
log = logging.getLogger(__name__)

import midgardmvc.lib.helpers as h

from webob.exc import HTTPFound

from paste.request import construct_url, get_cookies
from paste.auth import auth_tkt

from zope.interface import implements

from repoze.who.interfaces import IIdentifier
from repoze.who.interfaces import IAuthenticator

from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin, make_plugin as make_repoze_who_auth_tkt_plugin
from password import midgard_user_get
from midgardmvc.lib.midgard.connection import instance as connection_instance

_NOW_TESTING = None  # unit tests can replace
def _now():  #pragma NO COVERAGE
    if _NOW_TESTING is not None:
        return _NOW_TESTING
    return datetime.datetime.now()

class MidgardCookieAuth(AuthTktCookiePlugin):

    implements(IIdentifier, IAuthenticator)

    def __init__(self, authtype, secret, cookie_name='auth_tkt',
                 secure=False, include_ip=False,
                 timeout=None, reissue_time=None, userid_checker=None):
        super(MidgardCookieAuth, self).__init__(secret, cookie_name, secure, include_ip, timeout, reissue_time, userid_checker)
        
        self.authtype = authtype
    
    # IIdentifier
    def identify(self, environ):
        log.debug("cookieAuth identify")
        
        cookies = get_cookies(environ)
        cookie = cookies.get(self.cookie_name)

        if cookie is None or not cookie.value:
            return None

        if self.include_ip:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'
        
        try:
            timestamp, userid, tokens, user_data = auth_tkt.parse_ticket(
                self.secret, cookie.value, remote_addr)
        except auth_tkt.BadTicket:
            return None

        if self.timeout and ( (timestamp + self.timeout) < time.time() ):
            return None

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
        log.debug("cookieAuth remember")
        
        if self.include_ip:
            remote_addr = environ.get('REMOTE_ADDR', '0.0.0.0')
        else:
            remote_addr = '0.0.0.0'

        cookies = get_cookies(environ)
        old_cookie = cookies.get(self.cookie_name)
        existing = cookies.get(self.cookie_name)
        old_cookie_value = getattr(existing, 'value', None)
        max_age = identity.get('max_age', None)

        timestamp, userid, tokens, userdata = None, '', '', ''

        if old_cookie_value:
            try:
                timestamp,userid,tokens,userdata = auth_tkt.parse_ticket(
                    self.secret, old_cookie_value, remote_addr)
            except auth_tkt.BadTicket:
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

        if old_data != new_data or (self.reissue_time and
                ( (timestamp + self.reissue_time) < time.time() )):
            ticket = auth_tkt.AuthTicket(
                self.secret,
                who_userid,
                remote_addr,
                tokens=who_tokens,
                user_data=who_userdata,
                cookie_name=self.cookie_name,
                secure=self.secure)
            new_cookie_value = ticket.cookie_value()
            
            cur_domain = environ.get('HTTP_HOST', environ.get('SERVER_NAME'))
            wild_domain = '.' + cur_domain
            if old_cookie_value != new_cookie_value:
                if "auth_remember_allow" in environ and environ["auth_remember_allow"] == False:
                    return None
                
                # return a set of Set-Cookie headers
                return self._get_cookies(environ, new_cookie_value, max_age)

    # IAuthenticator
    def authenticate(self, environ, identity):
        log.debug("cookieAuth authenticate")
        log.debug(identity)
        
        user_guid = identity.get('midgard.user.guid')
               
        if user_guid is None:
            return None

        if self.userid_checker and not self.userid_checker(user_guid):
            return None
        
        user = midgard_user_get(identity.get("login"),self.authtype, None)
        
        if not user:
            # Try to reopen db connection and then try again
            from midgardmvc.lib.midgard.connection import instance as connection_instance
            if connection_instance.reconnect():
                user = midgard_user_get(identity.get("login"), self.authtype, None)
        
        log.debug("user: ")
        log.debug(user)

        if not user:
            log.error("User %s (%s / %s) not found, reason: %s" % (user_guid, identity.get("login"), self.authtype, connection_instance.connection.get_error_string()))
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
            self.cookie_name, value, max_age)),
            ('Set-Cookie', '%s="%s"; Path=/; Domain=%s%s' % (
            self.cookie_name, value, cur_domain, max_age)),
            ('Set-Cookie', '%s="%s"; Path=/; Domain=%s%s' % (
            self.cookie_name, value, wild_domain, max_age))
            ]
        return cookies

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__,
                            id(self)) #pragma NO COVERAGE

def _bool(value):
    if isinstance(value, basestring):
        return value.lower() in ('yes', 'true', '1')
    return value

def make_plugin(authtype="Plaintext", secret=None,
                secretfile=None,
                cookie_name='auth_tkt',
                secure=False,
                include_ip=False,
                timeout=None,
                reissue_time=None,
                userid_checker=None,
               ):
    
    from repoze.who.utils import resolveDotted
    if (secret is None and secretfile is None):
        raise ValueError("One of 'secret' or 'secretfile' must not be None.")
    if (secret is not None and secretfile is not None):
        raise ValueError("Specify only one of 'secret' or 'secretfile'.")
    if secretfile:
        secretfile = os.path.abspath(os.path.expanduser(secretfile))
        if not os.path.exists(secretfile):
            raise ValueError("No such 'secretfile': %s" % secretfile)
        secret = open(secretfile).read().strip()
    if timeout:
        timeout = int(timeout)
    if reissue_time:
        reissue_time = int(reissue_time)
    if userid_checker is not None:
        userid_checker = resolveDotted(userid_checker)

    plugin = MidgardCookieAuth(authtype, secret,
                                cookie_name,
                                _bool(secure),
                                _bool(include_ip),
                                timeout,
                                reissue_time,
                                userid_checker,
                                )
    
    return plugin

