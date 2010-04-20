import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.i18n.translation import _

from midgardmvc.lib.base import BaseController, render
import midgardmvc.lib.helpers as h

log = logging.getLogger(__name__)

from midgardmvc.lib.midgard.auth.decorators import authenticated

class MainController(BaseController):
    
    @authenticated
    def index(self):
        c.page = h.midgard.mgdschema.midgard_page()
        page_found = c.page.get_by_path('/midcom_root')
        
        if page_found:
            c.title += ":: " + c.page.title
        else:
            c.title += ":: " + _("Frontpage")
        
        # Return a rendered template
        return render('/frontpage.mako')
