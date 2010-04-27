"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""

from pylons import url, request, response

from webhelpers.html import literal
from webhelpers.html.tags import *
from webhelpers.pylonslib.minify import stylesheet_link, javascript_link

from webhelpers.pylonslib import Flash as _Flash

import logging
log = logging.getLogger(__name__)

import _midgard as midgard
#from midgardmvc.lib.midgard.middleware import MIDGARD as midgard

flash = _Flash()

def flash_ok(message):
    flash(message, category='success')

def flash_info(message):
    flash(message, category='notice')

def flash_warning(message):
    flash(message, category='warning')
    
def flash_alert(message):
    flash(message, category='error')