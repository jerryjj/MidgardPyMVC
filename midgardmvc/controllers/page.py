import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.i18n.translation import _

from midgardmvc.lib.base import BaseController, render
import midgardmvc.lib.helpers as h

log = logging.getLogger(__name__)

class PageController(BaseController):

    def show(self, path):
        c.page = h.midgard.mgdschema.midgard_page()
        page_found = c.page.get_by_path(path)
        
        if not page_found:
            abort(404)
            
        c.title += ":: " + c.page.title
            
        return render('/page.mako')
