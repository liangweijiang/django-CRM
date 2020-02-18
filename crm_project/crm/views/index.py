#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import auth
from crm.forms import RegForm
from django.views import View
# from django.db.models import Q
from django.contrib.auth.decorators import login_required
from rbac.server.permission_init import permission_init
import random
from PIL import Image, ImageDraw, ImageFont


def index(request):
    if request.session.get('username'):
        username = request.session.get('username')
        return render(request, 'crm/logined_index.html', {'username': username})
    else:
        return render(request, 'index.html')


def random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def v_code(request):
    """
    处理验证码的函数
    :param request:
    :return:
    """
    img_obj = Image.new('RGB', (390, 35), random_color())
    # 生成画布
    draw_obj = ImageDraw.Draw(img_obj)
    # 字体的样式
    font_obj = ImageFont.truetype('static/font/kumo.ttf', 28)
    code_temp = []
    for i in range(5):
        lower = chr(random.randint(97, 122))
        upper = chr(random.randint(65, 90))
        number = str(random.randint(0, 9))
        choice = random.choice([lower, upper, number])
        code_temp.append(choice)
        draw_obj.text((i * 40 + 35, 0), choice, fill=random_color(), font=font_obj)

    # 加干扰线
    width = 390  # 图片宽度（防止越界）
    height = 35
    for i in range(5):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        draw_obj.line((x1, y1, x2, y2), fill=random_color())

    # 存入session, 方便验证
    request.session['v_code'] = ''.join(code_temp).upper()
    # 将图片加载进内存
    from io import BytesIO
    f1 = BytesIO()
    img_obj.save(f1, format="PNG")
    img_data = f1.getvalue()

    return HttpResponse(img_data, content_type='image/png')


def login(request):
    err_msg = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        v_code = request.POST.get('v_code').upper()
        if v_code == request.session['v_code']:
            obj = auth.authenticate(request, username=username, password=password)
            if obj:
                auth.login(request, obj)
                # 登录成功
                # 将权限信息写入到session
                permission_init(obj, request)
                return redirect(reverse('index'))
            else:
                err_msg = '用户名或密码错误'
        else:
            err_msg = '验证码错误'
    return render(request, 'login.html', {'error_msg': err_msg})


def register(request):
    form_obj = RegForm()
    if request.method == 'POST':
        form_obj = RegForm(request.POST)
        if form_obj.is_valid():
            # 创建新用户
            # 方法一
            # form_obj.cleaned_data.pop('re_password')
            # models.UserProfile.objects.create_user(**form_obj.cleaned_data)

            # 方法二
            obj = form_obj.save()
            obj.set_password(obj.password)
            obj.save()
            return redirect('/login/')
    return render(request, 'register.html', {'form_obj': form_obj})


# 用来验证是否已经登录
class LoginRequired(View):
    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super().as_view(*args, **kwargs)
        return login_required(view)


# # 模糊搜索
# class Search:
#     def __init__(self, query_list, request):
#         self.query_list = query_list
#         self.request = request
#
#     def get_search_info(self):
#         query = self.request.GET.get('query', '')
#         q = Q()
#         q.connector = 'OR'
#         for i in self.query_list:
#             q.children.append(Q(('{}__contains'.format(i), query)))
#         return q
