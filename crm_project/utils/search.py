#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db.models import Q


# 模糊搜索
class Search:
    def __init__(self, query_list, request):
        self.query_list = query_list
        self.request = request

    def get_search_info(self):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'
        for i in self.query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))
        return q
