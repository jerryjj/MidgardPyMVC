"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""

from pylons import url, request, response

from webhelpers.html import literal
from webhelpers.html.tags import *
from webhelpers.pylonslib.minify import stylesheet_link, javascript_link

from webhelpers.pylonslib import Flash as _Flash

import midgardmvc.lib.output.helpers.header as header

import logging
log = logging.getLogger(__name__)

from gi.repository import GObject, Midgard
from midgardmvc.lib.midgard.connection import instance as connection_instance

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

class midgard_legacy_query_builder():
  group = None
  qs = None
  
  def __init__(self, name):
    storage = Midgard.QueryStorage(dbclass = name)
    self.qs = Midgard.QuerySelect(connection = connection_instance.connection, storage = storage)
    self.qs.toggle_read_only(False)

  def add_constraint(self, name, operator, value):
    if self.group is None:
      self.group = Midgard.QueryConstraintGroup(grouptype = "AND")
    self.group.add_constraint(
      Midgard.QueryConstraint(
        property = Midgard.QueryProperty(property = "name"),
        operator = operator,
        holder = Midgard.QueryValue.create_with_value(value)
      )
    )

  def get_query_select(self):
    return self.qs

  def execute(self):
    if self.group is not None:
      self.qs.set_constraint(self.group)
    self.qs.execute()
    return self.qs.list_objects()

