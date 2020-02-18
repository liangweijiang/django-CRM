#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import HttpResponse
import re


class PermissionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        验证用户的权限
        """
        current_url = request.path_info
        for url in settings.WHITE_URL_LIST:
            if re.match(url, current_url):
                return
        permission_query = request.session.get(settings.PERMISSION_SESSION_KEY)
        # print(permission_query, type(permission_query))
        request.breadcrumb_list = [
            {"title": '首页', 'url': '#'}, ]
        try:
            for query in permission_query.values():
                url = query.get('url')
                # print(query)
                # print(url, current_url)
                if re.match("^{}".format(url), current_url):
                    id = query.get('id')
                    pid = query.get('pid')
                    p_name = query.get('p_name')
                    if pid:
                        # 表示当前权限是子权限，让父权限是展开
                        request.current_menu_id = pid
                        request.breadcrumb_list.extend(
                            [{"title": permission_query[p_name]['title'], 'url': permission_query[p_name]['url']},
                             {"title": query['title'], 'url': query['url']}]
                        )

                    else:
                        # 表示当前权限是父权限，要展开的二级菜单
                        request.current_menu_id = id
                        # 添加面包屑导航
                        request.breadcrumb_list.append({"title": query['title'], 'url': query['url']})
                    return
        except Exception as e:
            print(e)
        else:
            return HttpResponse('没有权限')