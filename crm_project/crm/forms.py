#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.forms import widgets
from crm import models
from django.core.exceptions import ValidationError


class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for filed in self.fields.values():
            filed.widget.attrs.update({'class': 'form-control'})


class RegForm(BaseForm):
    password = forms.CharField(
        label='密码',
        min_length=8,
        max_length=16,
        widget=widgets.PasswordInput(),
        error_messages={
            'min_length': '长度必须为8以上',
            'max_length': '长度不能超过,6位',
            'required': '不能为空',
        }
    )
    re_password = forms.CharField(
        label='确认密码',
        widget=forms.widgets.PasswordInput()
    )

    class Meta:
        model = models.UserProfile
        # fields = '__all__'   # 所有字段
        fields = ['username', 'password', 're_password', 'name', 'department']  # 指定字段
        # exclude = ['']
        widgets = {
            'username': forms.widgets.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.widgets.PasswordInput,
        }

        labels = {
            'username': '用户名',
            'password': '密码',
            'name': '姓名',
            'department': '部门',
        }

    def clean(self):
        pwd = self.cleaned_data.get('password')
        re_pwd = self.cleaned_data.get('re_password')
        if pwd == re_pwd:
            return self.cleaned_data
        self.add_error('re_password', '两次密码不一致')
        raise ValidationError('两次密码不一致')


# 客户form
class CustomerForm(BaseForm):
    class Meta:
        model = models.Customer
        exclude = ['class_type']
        widgets = {
            'course': forms.widgets.SelectMultiple
        }


# 跟进记录form
class ConsultRecordForm(BaseForm):
    class Meta:
        model = models.ConsultRecord
        # fields = '__all__'
        exclude = ['delete_status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # try:
        customer_choice = [(i.id, i) for i in self.instance.consultant.customers.all()]
        customer_choice.insert(0, ('', '请选择客户'))
        # 限制客户是当前销售的私户
        self.fields['customer'].widget.choices = customer_choice
        # 限制跟进人是当前的用户（销售）
        self.fields['consultant'].widget.choices = [(self.instance.consultant.id, self.instance.consultant), ]
        # except Exception as e:
        #     print('---------->', e)


class EnrollmentForm(BaseForm):
    class Meta:
        model = models.Enrollment
        exclude = ['delete_status', 'contract_approved']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 限制当前的客户只能是传的id对应的客户
        self.fields['customer'].widget.choices = [(self.instance.customer_id, self.instance.customer), ]
        # 限制当前可报名的班级是当前客户的意向班级
        self.fields['enrolment_class'].widget.choices = [(i.id, i) for i in self.instance.customer.class_list.all()]


# 班级Form
class ClassForm(BaseForm):
    class Meta:
        model = models.ClassList
        fields = '__all__'


# 课程记录Form
class CourseForm(BaseForm):
    class Meta:
        model = models.CourseRecord
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 限制当前的班级是传过来id的班级
        self.fields['re_class'].widget.choices = [(self.instance.re_class_id, self.instance.re_class)]
        # 限制当前的班主任是当前用户
        self.fields['teacher'].widget.choices = [(self.instance.teacher_id, self.instance.teacher)]


# 学习记录
class StudyRecordForm(BaseForm):
    class Meta:
        model = models.StudyRecord
        fields = ['attendance', 'score', 'homework_note', 'note', 'student']
