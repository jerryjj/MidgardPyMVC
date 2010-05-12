from decorator import decorator
import functools

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort
from pylons import config

def authenticated(method):
    """Decorate methods with this to require that the user be logged in."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        ignore_enabled_flag=False
        if not config["midgard.authentication.enabled"] and ignore_enabled_flag == False:
            return method(self)
        
        identity = request.environ.get('repoze.who.identity')
        if not identity:
            abort(401)
        
        return method(self)
    return wrapper