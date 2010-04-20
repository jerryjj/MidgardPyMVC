from decorator import decorator
import functools

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort

def authenticated(method):
    """Decorate methods with this to require that the user be logged in."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        identity = request.environ.get('repoze.who.identity')
        if not identity:
            abort(401)
        
        return method(self)
    return wrapper