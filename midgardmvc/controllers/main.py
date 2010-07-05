import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect
from pylons.i18n.translation import _

from midgardmvc.lib.base import BaseController, render
import midgardmvc.lib.helpers as h

from midgardmvc.lib.midgard.auth import get_active_user, get_active_user_person

log = logging.getLogger(__name__)

from midgardmvc.lib.midgard.auth.decorators import authenticated

class MainController(BaseController):
    
    def index(self):
        c.node = h.midgard.mgdschema.midgardmvc_core_node()
        node_found = c.node.get_by_path('/midcom_root')
        
        if node_found:
            c.title += ":: " + c.node.title
        else:
            c.title += ":: " + _("Frontpage")
        
        c.user = get_active_user()
        c.person = get_active_user_person()
        
        # Return a rendered template
        return render('/frontpage.mako')
