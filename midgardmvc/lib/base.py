"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render
from pylons import request, tmpl_context as c
from pylons.i18n.translation import _, set_lang

import midgardmvc.lib.helpers as h

class BaseController(WSGIController):
    def __before__(self, language="en"):
        c.title = _("Midgard CMS")
        
        h.header.addMeta(name="generator", value="MidgardPyMVC")
        
        if language:
            set_lang(language)

        c.language = language
    
    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        return WSGIController.__call__(self, environ, start_response)


class AjaxBaseController(BaseController):
    content_type = 'application/json'
    
    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        
        response.headers['Content-Type'] = self.content_type
        response.charset = 'utf8'
        
        return super(AjaxBaseController, self).__call__(environ, start_response)

class jQGridController(AjaxBaseController):
    def getGridParameters(self):
        page = int(request.POST.get('page', 1))
        limit = int(request.POST.get('rows', 10))
        sort_field = request.POST.get('sidx', '')
        sort_order = request.POST.get('sord', '').upper()
        
        return [page, limit, sort_field, sort_order]
    
    def searchParamsToQuery(self):
        if not request.POST.has_key('_search'):
            return None
        
        if not asBool(request.POST.get('_search')):
            return None
        
        filters = dict(
            groupOp = 'AND',
            rules = []
        )
        
        if request.POST.has_key('filters'):
            filters = simplejson.loads(request.POST.get('filters'))
        else:
            if (not request.POST.has_key('searchField')
                and not request.POST.has_key('searchOper')
                and not request.POST.has_key('searchString')):
                return None
            
            filters['rules'].append(dict(
                field = request.POST.get('searchField'),
                op = request.POST.get('searchOper'),
                data = request.POST.get('searchString'),
            ))
        
        filters['groupOp'] = filters['groupOp'].upper()
        
        query = []
        
        for rule in filters['rules']:
            operand = self._resolveSearchOperand(rule['op'])
            if not operand:
                continue
            
            query_part = []
            if filters['groupOp'] != 'AND':
                query_part.append('OR')
            
            query_part.append(rule['field'])
            
            field_value = rule['data']
            
            if isinstance(operand, basestring):
                query_part.append(operand)
            else:
                query_part.append(operand[0])
                field_value = operand[1] % field_value
            
            query_part.append(field_value)
            
            query.append(query_part)
        
        return query
    
    def _resolveSearchOperand(self, op):
        operands = {
            'eq': '=',
            'ne': '!=',
            'lt': '<',
            'le': '<=',
            'gt': '>',
            'ge': '>=',
            'bw': [
                'LIKE',
                '%s%'
            ],
            'bn': [
                'NOT LIKE',
                '%s%'
            ],
            'in': 'IN',
            'ni': 'NOT IN',
            'ew': [
                'LIKE',
                '%%s'
            ],
            'en': [
                'NOT LIKE',
                '%%s'
            ],
            'cn': 'LIKE',
            'nc': None
        }
        
        if operands.has_key(op):
            return operands[op]
        
        return None
