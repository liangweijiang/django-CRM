#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from collections import OrderedDict

register = template.Library()


@register.inclusion_tag('rbac/menu.html')
def menu(request):
    menu_dict = request.session.get(settings.MENU_SESSION_KEY)
    order_dict = OrderedDict()
    # print(menu_dict, type(menu_dict))
    for key in sorted(menu_dict, key=lambda x: menu_dict[x]['weight'], reverse=True):
        order_dict[key] = menu_dict[key]

        item = order_dict[key]

        item['class'] = 'hide'
        children = item.get('children')
        for child in children:
            # url = child.get('url')
            if child['id'] == request.current_menu_id:
                child['class'] = 'active'
                item['class'] = ''
                break
    return {'menu_dict': menu_dict}


@register.inclusion_tag('rbac/breadcrumb.html')
def breadcrumb(request):
    return {'breadcrumb_list': request.breadcrumb_list}


@register.filter
def has_permission(request, url):
    return url in request.session.get(settings.PERMISSION_SESSION_KEY)


@register.simple_tag
def gen_role_url(request, rid):
    params = request.GET.copy()
    params._mutable = True
    params['rid'] = rid
    return params.urlencode()
