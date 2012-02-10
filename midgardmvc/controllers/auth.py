import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.i18n.translation import _

from midgardmvc.lib.base import BaseController, render
import midgardmvc.lib.helpers as h

log = logging.getLogger(__name__)

class AuthController(BaseController):    
    def login(self):
        """ This is where the login form should be rendered. """
        
        # Number of times the user has tried to log in
        login_counter = request.environ.get('repoze.who.logins', 0)
        if login_counter > 0:
            h.flash_alert('Wrong credentials')
        
        c.login_counter = login_counter
        # Previous URL, if we were redirected to login by an unauhorized error
        c.came_from = request.params.get('came_from') or url("/")
        
        return render('/auth/login.mako')
    
    def post_login(self):
        """ This is where the user ends up with after a login attempt. """
        
        identity = request.environ.get('repoze.who.identity')
        came_from = str(request.params.get('came_from', '')) or url('/')
        if not identity:
            # The user provided the wrong credentials
            login_counter = request.environ['repoze.who.logins'] = request.environ.get('repoze.who.logins', 0) + 1
            redirect(url(controller='auth', action='login', came_from=came_from,
                                __logins=login_counter))
        
        person = identity['midgard.person']
        h.flash_ok('Welcome back, %s!' % person.get_property("firstname"))
        
        redirect(url(came_from))
    
    def post_logout(self):
        """ This is where the user ends up after logging out. """
        
        return render('/auth/post_logout')
