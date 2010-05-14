from midgardmvc.lib.helpers import midgard
from midgardmvc.model.midgard import resolveSchemaFields

import formencode

class FormSchema(formencode.Schema):
    """docstring for midgard_person FormSchema"""
    ignore_key_missing = True
    
    def __classinit__(cls, new_attrs):
        schema_fields = resolveSchemaFields(midgard.mgdschema.midgard_person)
        
        for name, field in schema_fields.iteritems():
            if field["type"] != "string":
                continue
            if cls.fields.has_key(name):
                continue
            cls.add_field(name, formencode.validators.String(not_empty=True))
        
        formencode.Schema.__classinit__(cls, new_attrs)