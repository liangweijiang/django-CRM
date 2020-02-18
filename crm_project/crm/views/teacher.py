#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, reverse, HttpResponse
from crm.views.index import LoginRequired
from crm.models import ClassList, CourseRecord, StudyRecord
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import auth
from crm.forms import ClassForm, CourseForm, StudyRecordForm
from django.utils.safestring import mark_safe
from utils.pagination import Pagination
from utils.search import Search
from django.views import View
from django.db.models import Q
from django.http import QueryDict
import copy
from django.db import transaction
import time
from django.conf import settings
from django.views import View


class ShowClassList(LoginRequired):
    """
    展示班级信息
    """

    def get(self, request):
        query_list = ['course', 'semester']
        q = Search(query_list, request).get_search_info()
        all_class = ClassList.objects.filter(q)
        query_params = copy.deepcopy(request.GET)
        page = Pagination(request, all_class.count(), query_params)
        query_params = self.get_query_params()
        return render(request, 'crm/teacher/class_list.html',
                      {'all_class': all_class[page.start:page.end],
                       'pagination': page.show_li,
                       'query_params': query_params
                       }
                      )

    def post(self, request):
        action = request.POST.get('action')
        print('----------->', action)
        if not hasattr(self, action):
            return HttpResponse('非法操作')

        ret = getattr(self, action)()

        if ret:
            return ret

        return self.get(request)

    # def get_search_info(self, query_list):
    #     query = self.request.GET.get('query', '')
    #     q = Q()
    #     q.connector = 'OR'
    #     for i in query_list:
    #         q.children.append(Q(('{}__contains'.format(i), query)))
    #     return q

    def get_query_params(self):
        """
         获取add按钮
        """
        qd = QueryDict()
        qd._mutable = True
        url = self.request.get_full_path()
        qd['next'] = url
        query_params = qd.urlencode()
        return query_params


# 添加,编辑班级
def class_list(request, edit_id=None):
    class_obj = ClassList.objects.filter(id=edit_id).first()
    form_obj = ClassForm(instance=class_obj)
    if request.method == 'POST':
        form_obj = ClassForm(request.POST, instance=class_obj)
        if form_obj.is_valid():
            form_obj.save()
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect(reverse('crm:class_list'))
    return render(request, 'crm/teacher/class.html', {'form_obj': form_obj})


# -----------------------------------------------------------------------------------
class ShowCourse(LoginRequired):
    """
        展示班级信息
    """

    def get(self, request, class_id):
        query_list = []
        q = Search(query_list, request).get_search_info()
        all_course = CourseRecord.objects.filter(q, re_class_id=class_id)
        query_params = copy.deepcopy(request.GET)
        page = Pagination(request, all_course.count(), query_params)
        query_params = self.get_query_params()

        return render(request, 'crm/teacher/course_list.html',
                      {'all_course': all_course[page.start:page.end],
                       'pagination': page.show_li,
                       'query_params': query_params,
                       'class_id': class_id
                       }
                      )

    def post(self, request, class_id):
        action = request.POST.get('action')
        if not hasattr(self, action):
            return HttpResponse('非法操作')

        ret = getattr(self, action)()

        if ret:
            return ret

        return self.get(request, class_id)

    def get_query_params(self):
        """
         获取query_params,相当于url后面的拼接参数
        """
        qd = QueryDict()
        qd._mutable = True
        url = self.request.get_full_path()
        qd['next'] = url
        query_params = qd.urlencode()
        return query_params

    def multi_init(self):
        """
        根据课程初始化学生的学习记录
        """
        course_ids = self.request.POST.getlist('id')
        course_obj_list = CourseRecord.objects.filter(id__in=course_ids)
        # 查询当前课程记录代表的班级的学生

        for course_obj in course_obj_list:
            all_students = course_obj.re_class.customer_set.filter(status='studying')
            student_list = []
            for student in all_students:
                # models.StudyRecord.objects.create(course_record=course_obj, student=student)
                # obj = models.StudyRecord(course_record=course_obj, student=student)
                # obj.save()
                student_list.append(StudyRecord(course_record=course_obj, student=student))
            StudyRecord.objects.bulk_create(student_list)


# 添加,编辑课程
def course_list(request, class_id=None, edit_id=None):
    class_obj = CourseRecord.objects.filter(id=edit_id).first() or CourseRecord(re_class_id=class_id,
                                                                                teacher=request.user)
    form_obj = CourseForm(instance=class_obj)
    if request.method == 'POST':
        form_obj = CourseForm(request.POST, instance=class_obj)
        if form_obj.is_valid():
            form_obj.save()
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect(reverse('crm:course_list', args=(class_id,)))
    return render(request, 'crm/teacher/course.html', {'form_obj': form_obj, 'active': 'active_class'})


# --------------------------------------------------------------------------------------------------------

# 展示和修改学习记录
from django.forms import modelformset_factory


def study_record(request, class_id,course_id):
    # modelformset_factory返回的是一个类
    FormSet = modelformset_factory(StudyRecord, StudyRecordForm, extra=0)
    queryset = StudyRecord.objects.filter(course_record_id=course_id)
    form_set = FormSet(queryset=queryset)
    if request.method == 'POST':
        form_set = FormSet(request.POST)
        if form_set.is_valid():
            form_set.save()
            return redirect(reverse('crm:course_list', args=(class_id,)))
    return render(request, 'crm/teacher/study_record_list.html', {"form_set": form_set, 'queryset': queryset})

