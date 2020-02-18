#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
权限的初始化
"""
from django.conf import settings
from django.shortcuts import HttpResponse


def permission_init(obj, request):
    try:
        permission_query = obj.user.roles.filter(permissions__url__isnull=False).values(
            'permissions__url',
            'permissions__title',
            'permissions__id',
            'permissions__name',
            'permissions__parent_id',
            'permissions__parent__name',
            'permissions__menu_id',
            'permissions__menu__title',
            'permissions__menu__icon',
            'permissions__menu__weight',
        ).distinct()
        # # 菜单的存放列表
        # menu_list = []
        # 存放菜单的信息
        menu_dict = {}
        # # 存放权限的列表
        # permission_list = []
        # 存放权限的列表
        permission_dict = {}
        # for item in permission_query:
        #     permission_list.append({'url': item.get('permissions__url')})
        #     if item['permissions__is_menu']:
        #         menu_list.append({
        #             'url': item.get('permissions__url'),
        #             'is_menu': item.get('permissions__url'),
        #             'icon': item.get('permissions__icon'),
        #             'title': item.get('permissions__title'),
        #         })
        for item in permission_query:
            permission_dict[item['permissions__name']] = {'url': item.get('permissions__url'),
                                                          'id': item['permissions__id'],
                                                          'title': item.get('permissions__title'),
                                                          'pid': item['permissions__parent_id'],
                                                          'p_name': item['permissions__parent__name'],
                                                          }
            menu_id = item['permissions__menu_id']
            if not menu_id:
                continue
            if menu_id not in menu_dict.keys():
                menu_dict[menu_id] = {
                    'title': item.get('permissions__menu__title'),
                    'icon': item.get('permissions__menu__icon'),
                    'weight': item.get('permissions__menu__weight'),
                    'children': [
                        {'title': item.get('permissions__title'), 'url': item.get('permissions__url'),
                         'id': item.get('permissions__id'), 'pid': item.get('permissions__parent_id')
                         }
                    ]
                }
            else:
                menu_dict.get(menu_id)['children'].append(
                    {'title': item.get('permissions__title'), 'url': item.get('permissions__url'),
                     'id': item.get('permissions__id'), 'pid': item.get('permissions__parent_id')
                     }
                )
        # 将权限信息写入到session
        request.session[settings.PERMISSION_SESSION_KEY] = permission_dict

        # 将菜单信息写入到session
        request.session[settings.MENU_SESSION_KEY] = menu_dict
    except Exception as e:
        return HttpResponse("您未用有角色!")
