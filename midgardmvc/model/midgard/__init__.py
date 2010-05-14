import re

def resolveSchemaFields(midgard_object, include_values=False):
    fields = dict()
    skip_fields = ["guid", "metadata"]
    
    for k in midgard_object.props:
        if k.name in skip_fields:
            continue
        
        field = dict(
            type=resolveFieldTypeFromGObject(k.__gtype__)
        )
        
        if include_values:
            field["value"] = midgard_object.__getattribute__(k.name)
        
        fields[k.name] = field
    
    return fields

def resolveFieldTypeFromGObject(gtype):
    if re.search("GParamString", str(gtype)):
        return "string"
    elif re.search("GParamUInt", str(gtype)):
        return "int"
    elif re.search("GParamBoxed", str(gtype)):
        return "datetime"
    
    return gtype