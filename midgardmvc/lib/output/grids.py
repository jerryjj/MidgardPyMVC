import webui.lib.helpers as h
from webui.lib.utils import odict

from webhelpers.html.builder import HTML, literal
import webhelpers.html.grid as grid

import simplejson

class DataGrid(grid.Grid):
    def __init__(self, *args, **kw):
        super(DataGrid, self).__init__(*args, **kw)
    
    def generate_header_link(self, column_number, column, label_text):
        """ This handles generation of link and then decides to call
        self.default_header_ordered_column_format 
        or 
        self.default_header_column_format 
        based on if current column is the one that is used for sorting or not
        """ 
        from pylons import url
        # this will handle possible URL generation
        request_copy = self.request.copy().GET
        if not self.order_column: 
            self.order_column = request_copy.pop("order_col", None)
        if not self.order_dir:
            self.order_dir = request_copy.pop("order_dir", 'asc')

        if column == self.order_column and self.order_dir == "asc":
            new_order_dir = "dsc"
        else:
            new_order_dir = "asc"

        url_href = url.current(order_col=column, order_dir=new_order_dir,
                               **request_copy)
        label_text = HTML.tag("a", href=url_href, c=label_text)
        # Is the current column the one we're ordering on?
        if column == self.order_column:
            return self.default_header_ordered_column_format(column_number,
                                                             column,
                                                             label_text)
        else:
            return self.default_header_column_format(column_number, column,
                                                     label_text)

class jQGrid(object):
    """
    docstring for jQGrid
    
    Example usage:
    
    In controller:
    
    grid_id = 'objects_grid'
    grid_pager_id = grid_id + '_pager'
    
    data_url = h.url("/__ajax/grids/objects")
    
    grid = jQGrid(dict(
        grid = dict(
            rownumbers = True,
            autowidth = False
        )
    ))
    grid.setTitle(_("Objects"))
    
    grid_headers = grid.getHeaders()
    grid_headers["uuid"] = dict(
        title = 'uuid',
        hidden = True
    )
    grid_headers["name"] = dict(
        title = _("Object name"),
        width = 120,
        sortable = True
    )
    
    grid.setHeaders(grid_headers)
    grid.enablePager(grid_pager_id)
    grid.enableNavGrid(grid_pager_id)
    
    grid.setDataSource(data_url, 'xml')
    
    grid.prepare(grid_id)
    
    c.grid = grid
    
    In template:
    ${c.grid}
    """
    defaults = dict(
        grid_id = None,
        pager_id = None,
        navgrid_id = None,
        visible = True,
        grid_init = dict(
            ui_theme_path = '/css/jquery_ui_themes/cupertino',
            modules = [],
        ),
        grid = dict(
            datatype = 'local',
            forceFit = False,
            rowNum = 10,
            #height = 150,
            #width = 300,
            autowidth = True,
            viewrecords = True,
            multiselect = False,
            rowList = [10, 20, 30],
            mtype = 'POST',
            rownumbers = False,
        ),
        nav_grid = {
            'refresh': True,
            'search': False,
            'view': False,
            'edit': False,
            'add': False,
            'del': False,
        },
    )
    
    def __init__(self, config):
        self.config = jQGrid.defaults.copy()
        
        if config:
            self.updateConfig(config)
        
        self.doc_ready = ""
        
        self.headers = None
        self.sub_headers = None
        
        self.data = None
        self.datas = []
        
        self._render_table = False
        
        self._is_subgrid = False
        self.prepared = False
        self.headers_sent = False

    def updateConfig(self, override):
        return merge_configs(self.config, override)
    
    def getGridId(self):
        return self.config.get("grid_id")
    
    def getPagerId(self):
        return self.config.get("pager_id")
    
    def hasPager(self):
        if self.config.get("pager_id"):
            return True
        return False
    
    def setTitle(self, title):
        self.config["grid"]["caption"] = title
    
    def getHeaders(self):
        if self.sub_headers:
            return self.sub_headers
        elif self.headers:
            return self.headers
        
        return odict()
    
    def setHeaders(self, headers, sub_grid=False):
        if sub_grid:
            self.sub_headers = headers
            
            if not self.config["grid"].has_key("subGridModel"):
                self.config["grid"]["subGridModel"] = [
                    dict(name = [], width = [])
                ]
        else:
            self.headers = headers
            
            if not self.config["grid"].has_key("colNames"):
                self.config["grid"]["colNames"] = []
            if not self.config["grid"].has_key("colModel"):
                self.config["grid"]["colModel"] = []
        
        allowed_keys = [
            'width', 'align', 'sorttype', 'sortable',
            'hidden', 'formoptions', 'editrules', 'editable', 'editoptions',
            'edittype',
        ]
        
        for key, header in self.headers.items():
            if not sub_grid:
                self.config["grid"]["colNames"].append(header["title"])
            
            col = dict(
                name = key,
                index = key
            )
            
            if header.has_key('name'):
                col['name'] = header['name']
            if header.has_key('index'):
                col['index'] = header['index']
            
            for ak in allowed_keys:
                if header.has_key(ak):
                    col[ak] = header[ak]
            
            if sub_grid:
                self.config['grid']['subGridModel'][0]['name'].append(header['title'])
                val = 0
                if col.has_key['width']:
                    val = col['width']
                self.config['grid']['subGridModel'][0]['width'].append(val)
            else:
                self.config['grid']['colModel'].append(col)
    
    def setDataSource(self, url, datatype='xml'):
        self.config['grid']['url'] = url
        self.config['grid']['datatype'] = datatype
        
        if datatype == 'xml':
            self.config['grid_init']['modules'].append('JsonXml.js')
        elif datatype == 'json':
            self.config['grid_init']['modules'].append('json2.js')
        
    def addData(self, data):
        self.config['grid']['datatype'] = 'local'
        
        self.data = data
    
    def sortBy(self, column, order='desc'):
        self.config['grid']['sortname'] = column
        self.config['grid']['sortorder'] = order
    
    def enablePager(self, id=None):
        if id:
            self.config['pager_id'] = id
        
        self.config['grid']['pager'] = "#%s" % self.config['pager_id']
    
    def enableNavGrid(self, navgrid_id, **opts):
        self.config['grid_init']['modules'].append('grid.common.js')
        self.config['grid_init']['modules'].append('grid.formedit.js')
        
        self.config['navgrid_id'] = navgrid_id
        if len(opts) > 0:
            self.config['nav_grid'] = merge_configs(self.config['nav_grid'], opts)
    
    def setNavGridActionConfig(action, config={}):
        current = None
        conf_key = "%s_config" % action
        
        if self.config['nav_grid'].has_key(conf_key):
            current = self.config['nav_grid'][conf_key]
        
        if current:
            config = merge_configs(current, config)
        
        self.config['nav_grid'][conf_key] = config
    
    def enableFooter(self, user_data_on_footer=False):
        self.config['grid']['footerrow'] = True
        self.config['grid']['userDataOnFooter'] = user_data_on_footer
    
    def generateErrorFunction(self):
        js = ("function(xhr,st,err) {"
            "if (parseInt(xhr.status) == 200) { return; }"
            "jQuery('#%(grid_id)s-errors').html(xhr.status+': '+xhr.statusText).show();"
            "/*end*/}") % {'grid_id': self.config['grid_id']}
        
        return js
    
    def prepare(self, id=None, send_headers=True):
        if id:
            self.config['grid_id'] = id
        
        if self._is_subgrid:
            self.config['grid']['loadError'] = self.generateErrorFunction()
        
        grid_id = self.config['grid_id']
        
        if not grid_id:
            return
        
        json_grid_config = simplejson.dumps(self.config['grid'])
        
        #TODO convert to Python
        """
        if (strpos($grid_config, '":"function')) {
            $grid_config = str_replace('\/*', '/*', $grid_config);
            $grid_config = str_replace('*\/', '*/', $grid_config);
            
            $grid_config = preg_replace('/":"function(\(.*\)) \{(.*)\/\*end\*\/\}",/i', '":function$1{$2},', $grid_config);
            $grid_config = preg_replace('/":"function(\(.*\)) \{(.*)\/\*end\*\/\}"/i', '":function$1{$2}', $grid_config);
            $grid_config = str_replace('\"', '"', $grid_config);
            $grid_config = str_replace('\\\/', '/', $grid_config);
        }
        """
        
        js = "jQuery('#%(grid_id)s').jqGrid(%(grid_config)s)" % {'grid_id': grid_id, 'grid_config': json_grid_config}
        
        if self.config['navgrid_id']:
            edit_config, add_config, del_config, search_config, view_config = self._getNavGridActionConfigs()
            
            navgrid_config = simplejson.dumps(self.config['nav_grid'])
            
            js += ".navGrid('#%s',%s,%s,%s,%s,%s,%s)" % (
                self.config['navgrid_id'], navgrid_config, edit_config, add_config, del_config, search_config, view_config
            )        
        
        js += ";\n"
        
        self.doc_ready = js
        
        self._prepareLocalData()
        if self.config['grid']['datatype'] == 'local' and not self._render_table:
            for i, item in self.datas.items():
                json_data = simplejson.dumps(item)
                self.doc_ready += "jQuery('#%s').addRowData(%d, %s);\n" % (grid_id, i, json_data)        
        
        self.prepared = True
        
        if send_headers:
            self.sendHeaders()
    
    def render(self, id=None):
        if not self.prepared:
            self.prepare(id)
        
        self._resetData()
        
        return self.sendOutput()
    
    def sendOutput(self):
        html = literal("""\
        <div id="%(grid_id)s_holder" class="jqgrid_holder" style="%(holder_css)s">
            <div id="%(grid_id)s-errors" style="display: none;"></div>
            <table id="%(grid_id)s" cellpadding="0" cellspacing="0"></table>
            <div id="%(grid_pager_id)s"></div>
        </div>
        """)
        
        return html % {'grid_id': self.config['grid_id'], 'grid_pager_id': self.config['pager_id'], 'holder_css': ''}
    
    def sendHeaders(self):
        if self.headers_sent:
            return
        
        h.header.enablejQueryGrid(self.config['grid_init'])
        
        h.header.startElementGroup('jQueryGrid')
        
        h.header.addDocready(self.doc_ready)
        
        h.header.endElementGroup('jQueryGrid')
        
        self.headers_sent = True
    
    def getInitJS():
        return h.header.getGroupElements('jQueryGrid')
    
    def __html__(self):
        return self.render()
    
    def __str__(self):
        return self.__html__()
    
    def _resetData(self):
        self.headers = None
        self.config['grid']['colModel'] = []
        self.config['grid']['colNames'] = []
    
    def _getNavGridActionConfigs(self, encode=True):
        confs = {
            'edit': {},
            'add': {},
            'del': {},
            'search': {},
            'view': {},
        }
        json_confs = confs.copy()
        
        if self.config['nav_grid'].has_key('edit_config'):
            confs['edit'] = self.config['nav_grid'].pop('edit_config')
        if self.config['nav_grid'].has_key('add_config'):
            confs['add'] = self.config['nav_grid'].pop('add_config')
        if self.config['nav_grid'].has_key('del_config'):
            confs['del'] = self.config['nav_grid'].pop('del_config')
        if self.config['nav_grid'].has_key('search_config'):
            confs['search'] = self.config['nav_grid'].pop('search_config')
        if self.config['nav_grid'].has_key('view_config'):
            confs['view'] = self.config['nav_grid'].pop('view_config')
        
        if not encode:
            return [confs['edit'], confs['add'], confs['del'], confs['search'], confs['view']]
        
        for k, conf in confs.items():
            json_confs[k] = simplejson.dumps(conf)
        
        return [json_confs['edit'], json_confs['add'], json_confs['del'], json_confs['search'], json_confs['view']]
    
    def _prepareLocalData(self):
        if not self.data:
            return
        
        self.datas = []
        
        for item in self.data:
            data = dict()
            for key in self.headers:
                data[key] = None
                
                if item.has_key(key):
                    data[key] = item[key]
            
            self.datas.append(data)
        
        
def merge_configs(original, override):
    if not isinstance(original, dict):
        original = dict()

    if not isinstance(override, dict):
        return override

    for key, value in override.iteritems():
        if isinstance(value, dict):
            original[key] = merge_configs(original.get(key, dict()), value)
        else:
            original[key] = value

    return original