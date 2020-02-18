#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from rbac import views

urlpatterns = [
    url(r'^role/list/$', views.role_list, name='role_list'),
    url(r'^role/add/$', views.role, name='add_role'),
    url(r'^role/edit/(?P<rid>\d+)/$', views.role, name='edit_role'),
    url(r'^role/del/(?P<rid>\d+)/$', views.role_del, name='del_role'),

    url(r'^menu/list/$', views.menu_list, name='menu_list'),
    url(r'^menu/add/$', views.menu, name='add_menu'),
    url(r'^menu/edit/(?P<mid>\d+)/$', views.menu, name='edit_menu'),
    url(r'^menu/del/(?P<mid>\d+)/$', views.menu_del, name='del_menu'),

    url(r'^permission/add/$', views.permission, name='add_permission'),
    url(r'^permission/edit/(\d+)$', views.permission, name='edit_permission'),
    url(r'^permission/del/(\d+)$', views.permission_del, name='del_permission'),

    # 权限批量操作
    url(r'^multi/permissions/$', views.multi_permissions, name='multi_permissions'),
    # 权限分配
    url(r'^distribute/permissions/$', views.distribute_permissions, name='distribute_permissions'),

]