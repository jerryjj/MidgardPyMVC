from pylons import request

import re
import simplejson

from midgardmvc.lib.midgard.middleware import helper_stack

def getElements(only_group=None):
    ret = ""
    
    if helper_stack['header_data']['jquery_enabled']:
        ret += helper_stack['header_data']['jquery_inits']
    
    if only_group:
        ret += getGroupElements(only_group)
        return ret
    
    for name in helper_stack['header_data']['element_groups']:
        ret += getGroupElements(name)
    
    return ret

def getGroupElements(name):
    html = ''
    
    if helper_stack['header_data']['head_datas']['prepend_script'].has_key(name):
        for js_call in helper_stack['header_data']['head_datas']['prepend_script'].get(name, []):
            html += js_call
    
    if helper_stack['header_data']['head_datas']['js'].has_key(name):
        for js_call in helper_stack['header_data']['head_datas']['js'].get(name, []):
            html += js_call
            
    if helper_stack['header_data']['head_datas']['script'].has_key(name):
        for script in helper_stack['header_data']['head_datas']['script'].get(name, []):
            html += script + "\n"
            
    if helper_stack['header_data']['head_datas']['jquery_states'].has_key(name):
        html += "<script type=\"text/javascript\">\n/*<![CDATA[*/\n"
        html += "\njQuery(document).ready(function() {\n"
        html += helper_stack['header_data']['head_datas']['jquery_states'].get(name, "")
        html += "\n});\n"
        html += "/*]]>*/\n</script>\n"
    
    if helper_stack['header_data']['head_datas']['link'].has_key(name):
        for link in helper_stack['header_data']['head_datas']['link'].get(name, []):
            html += link + "\n"
            
    if helper_stack['header_data']['head_datas']['meta'].has_key(name):
        for meta in helper_stack['header_data']['head_datas']['meta'].get(name, []):
            html += meta + "\n"
    
    return html

def startElementGroup(name):    
    helper_stack['header_data']['active_element_group'] = name
    
    if not name in helper_stack['header_data']['element_groups']:
        helper_stack['header_data']['element_groups'].append(name)

def endElementGroup(name):
    helper_stack['header_data']['active_element_group'] = helper_stack['header_data']['prev_element_group']
    helper_stack['header_data']['prev_element_group'] = name

def removeElementGroup(name):
    if not name in helper_stack['header_data']['element_groups']:
        return
    
    if name == helper_stack['header_data']['active_element_group']:
        helper_stack['header_data']['active_element_group'] = None
        
    if name == helper_stack['header_data']['prev_element_group']:
        helper_stack['header_data']['prev_element_group'] = None
        
    for sect in helper_stack['header_data']['head_datas']:
        helper_stack['header_data']['head_datas'][sect].pop(name)
    
    helper_stack['header_data']['element_groups'].pop(name)

def getActiveElementGroup():
    if not helper_stack['header_data']['active_element_group']:
        if not 'default' in helper_stack['header_data']['element_groups']:
            helper_stack['header_data']['element_groups'].append('default')
        return 'default'
    
    return helper_stack['header_data']['active_element_group']

def enablejQuery(version='1.3.2'):
    if helper_stack['header_data']['jquery_enabled']:
        return
    
    helper_stack['header_data']['jquery_inits'] = "<script type=\"text/javascript\" src=\"/midcom-static/midgardmvc_core/js/jquery-%s.js\"></script>\n" % version
    
    helper_stack['header_data']['jquery_enabled'] = True

def enablejQueryUI(theme_path, mod='all', version='1.7.2'):
    if helper_stack['header_data']['jquery_ui_enabled']:
        return
    
    if not helper_stack['header_data']['jquery_enabled']:
        enablejQuery()
    
    helper_stack['header_data']['jquery_ui_enabled_version'] = version
    
    loadjQueryUITheme(theme_path, version)
    
    startElementGroup('jQueryUI')
    
    addJSFile("/midcom-static/midgardmvc_core/js/ui/%s/ui.core.js" % version, True)
    
    endElementGroup('jQueryUI')
    
    helper_stack['header_data']['jquery_ui_enabled'] = True
    
    if mod == 'all':
        loadjQueryUIPart('interactions', version)
        loadjQueryUIPart('effects', version)
        loadjQueryUIPart('widgets', version)
    elif mod == 'normal':
        loadjQueryUIPart('interactions', version)
        loadjQueryUIPart('effects', version)
        loadjQueryUIPart('ui.dialog', version)
        loadjQueryUIPart('ui.slider', version)
        loadjQueryUIPart('ui.datepicker', version)
        loadjQueryUIPart('ui.progressbar', version)
    elif mod == 'effects':
        loadjQueryUIPart('effects', version)

def loadjQueryUIPart(name, version='1.7.2'):
    if not helper_stack['header_data']['jquery_ui_enabled']:
        return False
    
    if name in helper_stack['header_data']['jquery_ui_loaded_parts']:
        return False
    
    startElementGroup('jQueryUI-parts')
    
    files_to_load = []
    load_after = []
    
    if name in ['core', 'ui.core']:
        return False
    elif name == 'effects':
        helper_stack['header_data']['jquery_ui_loaded_parts'].append('effects')
        
        if 'effects.core' not in helper_stack['header_data']['jquery_ui_loaded_parts']:
            load_after.append('effects.core')
        
        files_to_load = [
            'effects.blind', 'effects.bounce',
            'effects.clip', 'effects.drop', 'effects.explode',
            'effects.fold', 'effects.highlight', 'effects.pulsate',
            'effects.scale', 'effects.shake', 'effects.slide',
            'effects.transfer'
        ]
    elif name == 'interactions':
        helper_stack['header_data']['jquery_ui_loaded_parts'].append('interactions')
        
        files_to_load = [
            'ui.draggable', 'ui.droppable', 'ui.resizable', 
            'ui.selectable', 'ui.sortable'
        ]
    elif name == 'widgets':
        helper_stack['header_data']['jquery_ui_loaded_parts'].append('widgets')
        
        files_to_load = [
            'ui.accordion', 'ui.datepicker', 'ui.dialog', 
            'ui.progressbar', 'ui.slider', 'ui.tabs'
        ]
    else:
        if 'effects.core' not in helper_stack['header_data']['jquery_ui_loaded_parts'] and name != 'effects.core' and re.match('effects', name):
            load_after.append('effects.core')
        
        helper_stack['header_data']['jquery_ui_loaded_parts'].append(name)
        files_to_load.append(name)
    
    for filename in files_to_load:
        addJSFile("/midcom-static/midgardmvc_core/js/ui/%s/%s.js" % (version, filename), True)
    
    for name in load_after:
        loadjQueryUIPart(name, version)

    endElementGroup('jQueryUI-parts')

def loadjQueryUITheme(style_path=None, version='1.7.2'):
    startElementGroup('jQueryUI-theme')
    
    if not style_path:
        style_path = '/midcom-static/midgardmvc_core/css/jquery_ui_themes/cupertino'
    
    addLinkHead(rel = 'stylesheet', type = 'text/css', media = 'screen', href = "%s/jquery-ui-%s.css" % (style_path, version))
    
    endElementGroup('jQueryUI-theme')

def enablejQueryGrid(opts):
    if helper_stack['header_data']['jquery_grid_enabled']:
        return
    
    if len(opts) == 0:
        opts = {}
    
    if not helper_stack['header_data']['jquery_ui_enabled']:
        ui_theme_path = opts.get('ui_theme_path', '/midcom-static/midgardmvc_core/css/jquery_ui_themes/cupertino')
        
        enablejQueryUI(ui_theme_path, 'normal')
    
    startElementGroup('jQueryGrid')
    
    addJSFile("/midcom-static/midgardmvc_core/js/jquery.jqGrid.js", True)
    addLinkHead(rel = 'stylesheet', type = 'text/css', media = 'screen', href = "/midcom-static/midgardmvc_core/css/jqGrid/ui.jqgrid.css")
    addLinkHead(rel = 'stylesheet', type = 'text/css', media = 'screen', href = "/midcom-static/midgardmvc_core/css/jqGrid/jquery.searchFilter.css")
    
    #Fix me: This has to be taken from globals or environment
    lang_str = 'en'
    if opts.has_key('locale'):
        lang_str = opts['locale']
    
    modules = []
    if opts.has_key('modules'):
        modules.extend(opts['modules'])
        modules = _unify_list(modules)
    
    json_modules = simplejson.dumps(modules)
    
    js_path = '/midcom-static/midgardmvc_core/js/jqGrid/js/'
    
    config_str = "locale: '%s', jspath: '%s', modules: %s" % (lang_str, js_path, json_modules)
    
    script = "jqGridIncludeConfig = {%s};" % config_str    
    addScript(script, True)
    
    helper_stack['header_data']['jquery_grid_enabled'] = True
    
    endElementGroup('jQueryGrid')

def addDocready(script):
    group = getActiveElementGroup()
    
    if not helper_stack['header_data']['head_datas']['jquery_states'].has_key(group):
        helper_stack['header_data']['head_datas']['jquery_states'][group] = ""
    
    js_call = script.strip() + "\n"
    
    helper_stack['header_data']['head_datas']['jquery_states'][group] += js_call

def addJSFile(url, prepend=False):
    url = url.replace('&', '&amp;')
    url = url.replace('&amp;amp', '&amp;')
    
    if url in helper_stack['header_data']['js_head_urls']:
        return
    
    group = getActiveElementGroup()
    
    if not helper_stack['header_data']['head_datas']['js'].has_key(group):
        helper_stack['header_data']['head_datas']['js'][group] = []
    
    js_call = "<script type=\"text/javascript\" src=\"%s\"></script>\n" % url
    if prepend:
        helper_stack['header_data']['head_datas']['js'][group].reverse()
        helper_stack['header_data']['head_datas']['js'][group].append(js_call)
        helper_stack['header_data']['head_datas']['js'][group].reverse()
    else:
        helper_stack['header_data']['head_datas']['js'][group].append(js_call)
    
    helper_stack['header_data']['js_head_urls'].append(url)

def addScript(script, prepend=False, type='text/javascript', defer=''):
    group = getActiveElementGroup()
    
    if not helper_stack['header_data']['head_datas']['prepend_script'].has_key(group):
        helper_stack['header_data']['head_datas']['prepend_script'][group] = []

    if not helper_stack['header_data']['head_datas']['script'].has_key(group):
        helper_stack['header_data']['head_datas']['script'][group] = []
    
    js_call = "<script type=\"%s\"%s>\n/*<![CDATA[*/\n" % (type, defer)
    js_call += script.strip() + "\n"
    js_call += "/*]]>*/\n</script>\n"
    
    if prepend:
        helper_stack['header_data']['head_datas']['prepend_script'][group].append(js_call)
    else:
        helper_stack['header_data']['head_datas']['script'][group].append(js_call)

def addMeta(**opts):
    if not opts.has_key('name'):
        return False
    
    group = getActiveElementGroup()
    
    if not helper_stack['header_data']['head_datas']['meta'].has_key(group):
        helper_stack['header_data']['head_datas']['meta'][group] = []
    
    output = '<meta '
    output += " ".join('%s="%s"' % (k, v) for k, v in opts.items())
    output += "/>\n"
    
    helper_stack['header_data']['head_datas']['meta'][group].append(output)

def addLinkHead(**opts):
    prepend = opts.pop('prepend', False)
    
    if not opts.has_key('href'):
        return False
    
    if opts['href'] in helper_stack['header_data']['link_head_urls']:
        return False

    helper_stack['header_data']['link_head_urls'].append(opts['href'])
    
    output = ''
    
    had_conditions = False
    if opts.has_key('conditions'):
        had_conditions = True
        output += "<!--[if %s]>\n" % opts.pop('conditions')
    
    output += '<link '    
    output += " ".join('%s="%s"' % (k, v) for k, v in opts.items())    
    output += "/>\n"
    
    if had_conditions:
        output += "<![endif]-->\n"
    
    group = getActiveElementGroup()
    
    if not helper_stack['header_data']['head_datas']['link'].has_key(group):
        helper_stack['header_data']['head_datas']['link'][group] = []
    
    if prepend:
        helper_stack['header_data']['head_datas']['link'][group].reverse()
        helper_stack['header_data']['head_datas']['link'][group].append(output)
        helper_stack['header_data']['head_datas']['link'][group].reverse()
    else:
        helper_stack['header_data']['head_datas']['link'][group].append(output)
    
    return True

def addStyleLink(**opts):    
    prepend = opts.pop('prepend', False)
    
    if not opts.has_key('href'):
        return False

    opts['rel'] = 'stylesheet'
    opts['type'] = 'text/css'

    if not opts.has_key('media'):
        opts['media'] = 'all'

    return addLinkHead(**opts)


def _unify_list(seq, idfun=None): 
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result