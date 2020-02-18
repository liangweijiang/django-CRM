#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from crm.views import consult, teacher

urlpatterns = [
    # url(r'^show_customer/', views.show_customer, name='customer_list'),
    url(r'^show_customer/', consult.ShowCustomer.as_view(), name='customer_list'),
    # url(r'^show_customer/', views.show_customer, name='customer_list'),
    url(r'^my_customer/', consult.ShowCustomer.as_view(), name='my_customer'),
    # url(r'^add_customer/', views.add_customer, name='add_customer'),
    # 增加客户
    url(r'^customer/add/', consult.customer, name='add_customer'),
    # 编辑客户
    url(r'^customer/edit/(\d+)/', consult.customer, name='edit_customer'),
    # ----------------------------------------------------------------------------

    # 跟进记录
    # url(r'^show_consult_record/(\d+)/', views.show_consult_record, name='consult_record'),
    url(r'^show_consult_record/(\d+)/', consult.ShowConsultRecord.as_view(), name='consult_record'),
    # 增加跟进记录
    # url(r'^add_consult_record/', views.add_consult_record, name='add_consult_record'),
    url(r'^add_consult_record/', consult.consult_record, name='add_consult_record'),
    # 编辑跟进记录
    # url(r'^edit_consult_record/(\d+)', views.edit_consult_record, name='edit_consult_record'),
    url(r'^edit_consult_record/(\d+)/', consult.consult_record, name='edit_consult_record'),
    # ----------------------------------------------------------------------------------

    # 展示报名表
    url(r'^show_enrollment/(\d+)/', consult.ShowEnrollment.as_view(), name='enrollment'),
    # 添加报名表
    url(r'^add_enrollment/(?P<customer_id>\d+)/', consult.enrollment, name='add_enrollment'),
    # 编辑报名表
    url(r'^edit_enrollment/(?P<edit_id>\d+)/', consult.enrollment, name='edit_enrollment'),

    # -----------------------------------------------------------------------------------------

    # 展示某个班级的课程记录
    url(r'show_class/', teacher.ShowClassList.as_view(), name='class_list'),
    url(r'add_class/', teacher.class_list, name='add_class'),
    url(r'edit_class/(\d+)/', teacher.class_list, name='edit_class'),

    # ------------------------------------------------------------------------------------

    # 课程有关的url
    url(r'show_course/(\d+)/', teacher.ShowCourse.as_view(), name='course_list'),
    url(r'add_course/(?P<class_id>\d+)/', teacher.course_list, name='add_course'),
    url(r'edit_course/(?P<edit_id>\d+)/', teacher.course_list, name='edit_course'),

    # ----------------------------------------------------------------------------------
    # 学习记录有关url
    url(r'study_record_list/(?P<class_id>\d+)/(?P<course_id>\d+)/', teacher.study_record, name='study_record'),


]
