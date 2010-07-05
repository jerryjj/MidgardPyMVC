import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect
from pylons.i18n.translation import _

from midgardmvc.lib.base import BaseController, render
import midgardmvc.lib.helpers as h

log = logging.getLogger(__name__)

class NodeController(BaseController):

    def show(self, path):
        c.node = h.midgard.mgdschema.midgardmvc_core_node()
        node_found = c.node.get_by_path(path)
        
        if not node_found:
            abort(404)
            
        c.title += ":: " + c.node.title
            
        return render('/node.mako')
