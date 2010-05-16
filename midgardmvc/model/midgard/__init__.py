from midgardmvc.lib.helpers import midgard
import formencode

default_skip_fields = ["action", "id", "guid", "metadata"]

class MidgardFormSchema(formencode.Schema):
    """docstring for Midgard object FormSchema"""
    mgd_schema_name = None
    ignore_key_missing = True
    
    def __classinit__(cls, new_attrs):
        if cls.mgd_schema_name:
            model = eval("midgard.mgdschema.%s" % cls.mgd_schema_name)
            schema_fields = resolveSchemaFields(model)

            for name, field in schema_fields.iteritems():            
                if field["type"] != "string":
                    continue
                if cls.fields.has_key(name):
                    continue
                cls.add_field(name, formencode.validators.String(not_empty=True))
        
        formencode.Schema.__classinit__(cls, new_attrs)

def resolveSchemaFields(midgard_object, include_values=False, skip_fields=None, only_fields=None):
    fields = dict()
    
    if not skip_fields:
        skip_fields = default_skip_fields
    
    try:
        mgd_obj_name = midgard_object.__name__
    except AttributeError:
        mgd_obj_name = midgard_object.__class__.__name__
    
    rp = midgard.reflection_property(mgd_obj_name)
    
    for f in midgard_object.props:
        if f.name in skip_fields:
            continue
        
        if only_fields and not f.name in only_fields:
            continue
        
        field = _propertyToField(rp, f)
        
        if include_values:
            field["value"] = midgard_object.__getattribute__(f.name)
        
        fields[f.name] = field
    
    return fields

def _propertyToField(reflector, prop):
    field = dict(
        label=prop.name,
        description=reflector.description(prop.name),
        type=None,
        properties=dict(),
        value=None
    )
    
    gtype_int = reflector.get_midgard_type(prop.name)

    if gtype_int in [midgard.TYPE_STRING, midgard.TYPE_GUID]:
        field["type"] = "string"
    elif gtype_int == midgard.TYPE_LONGTEXT:
        field["type"] = "text"
        field["properties"]["contenttype"] = reflector.get_user_value(prop.name, "contenttype")
    elif gtype_int in [midgard.TYPE_INT, midgard.TYPE_UINT]:
        field["type"] = "integer"
    elif gtype_int == midgard.TYPE_FLOAT:
        field["type"] = "float"
    elif gtype_int == midgard.TYPE_BOOLEAN:
        field["type"] = "boolean"
    elif gtype_int == midgard.TYPE_TIMESTAMP:
        field["type"] = "datetime"    
    
    return field

def resolveMetadataFields(midgard_object, include_values=False, skip_fields=None, only_fields=None):
    fields = dict()
        
    try:
        metadata = midgard_object.metadata
    except AttributeError:
        metadata = midgard.mgdschema.metadata
    
    rp = midgard.reflection_property("midgard_metadata")
    
    for f in metadata.props:                
        if skip_fields and f.name in skip_fields:
            continue        
        if only_fields and not f.name in only_fields:
            continue
        
        field = _propertyToField(rp, f)
        
        if include_values:
            field["value"] = metadata.__getattribute__(f.name)
        
        fields[f.name] = field
    
    return fields