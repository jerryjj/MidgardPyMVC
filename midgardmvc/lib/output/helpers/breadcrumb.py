from midgardmvc.lib.midgard.middleware import helper_stack

class BreadcrumbData(object):
    """docstring for BreadcrumbData"""
    def __init__(self, config = None):
        super(BreadcrumbData, self).__init__()

    def addItem(self, path, title, _class = None):
        helper_stack['breadcrumb_data'].append({'path':path, 'title':title, 'class':_class})
    
    def getItems(self):
        return helper_stack['breadcrumb_data']


class BreadcrumbRenderer(object):
    """docstring for BreadcrumbRenderer"""
    _defaults = dict(
        separator = '&raquo;',
        skip_items = 0
    )

    def __init__(self, data, config = None):
        super(BreadcrumbRenderer, self).__init__()
        self.data = data
        self.config = BreadcrumbRenderer._defaults
        if config:
            self.config.update(config)
    
    def __html__(self):
        items = self.data.getItems()
        breadcrumb_len = len(items)
        counter = 0
        breadcrumb_str = ''
        for breadcrumb_item in items:
            counter = counter + 1
            if counter == breadcrumb_len:
                breadcrumb_str += breadcrumb_item['title']
            else:
                breadcrumb_str += '<a href="'+ breadcrumb_item['path'] + '">' + breadcrumb_item['title'] + '</a>&nbsp;' + self.config['separator'] + '&nbsp;'
        return breadcrumb_str
    
    def __str__(self):
        return __html__()
    
def simple_breadcrumb(data_config = None, renderer_config = None):
    return BreadcrumbRenderer(BreadcrumbData(data_config), renderer_config)