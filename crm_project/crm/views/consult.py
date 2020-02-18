from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib.auth.decorators import login_required
from crm.models import Customer, ConsultRecord, Enrollment
from crm.forms import CustomerForm, ConsultRecordForm, EnrollmentForm
from utils.pagination import Pagination
from utils.search import Search
from crm.views.index import LoginRequired
from django.http import QueryDict
import copy
from django.db import transaction
from django.conf import settings


# Create your views here.


# --------------------------------------------------------------------------


def show_customer(request):
    print('------------->', request.POST)
    if request.path_info == reverse('crm:customer_list'):
        customers = Customer.objects.filter(consultant__isnull=True)
        customers_msg = 1
    else:
        customers = Customer.objects.filter(consultant=request.user)
        customers_msg = 0
    page = Pagination(request, customers.count(), 2)
    return render(request, 'crm/consult/customer_list.html',
                  {'all_customer': customers, 'pagination': page.show_li, 'customers_msg': customers_msg,
                   'username': request.user})


# 展示客户CBV模式
class ShowCustomer(LoginRequired):
    def get(self, request):
        # query_list = [filed.name for filed in CustomerForm()]
        # q = self.get_search_contion(query_list)
        query_list = ['qq', 'name', 'last_consult_date', 'phone', 'sex']
        q = Search(query_list, request).get_search_info()
        if request.path_info == reverse('crm:customer_list'):
            customers = Customer.objects.filter(q, consultant__isnull=True)
            customers_msg = 1
        else:
            customers = Customer.objects.filter(q, consultant=request.user)
            customers_msg = 0
        query_params = copy.deepcopy(request.GET)
        page = Pagination(request, customers.count(), query_params)
        add_btn, query_params = self.get_add_btn()

        return render(request, 'crm/consult/customer_list.html',
                      {'all_customer': customers[page.start:page.end], 'pagination': page.show_li,
                       'customers_msg': customers_msg,
                       'add_btn': add_btn,
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

    def multi_apply(self):
        """
        公户变为私户
        """
        ids = self.request.POST.getlist('choice_id')
        apply_num = len(ids)
        if self.request.user.customers.count() + apply_num > settings.CUSTOMER_MAX_NUM:
            return HttpResponse('做人不要太贪心，给别人的机会')
        with transaction.atomic():
            # 方法一
            # Customer.objects.filter(id__in=ids).update(consultant=self.request.user)
            # 方法二
            cumstomer_objs = Customer.objects.filter(id__in=ids, consultant__isnull=True)
            if len(cumstomer_objs) == apply_num:
                self.request.user.customers.add(*cumstomer_objs)
            else:
                return HttpResponse('已有人拿取了该公户')

    def multi_public(self):
        """
        私户变公户
        :return:
        """
        ids = self.request.POST.getlist('choice_id')
        # 方法一
        # models.Customer.objects.filter(id__in=ids).update(consultant=None)
        # 方法二
        self.request.user.customers.remove(*Customer.objects.filter(id__in=ids))

    # def get_search_info(self, query_list):
    #     query = self.request.GET.get('query', '')
    #     q = Q()
    #     q.connector = 'OR'
    #     for i in query_list:
    #         q.children.append(Q(('{}__contains'.format(i), query)))
    #     return q

    def get_add_btn(self):
        """
         获取add按钮
        """
        qd = QueryDict()
        qd._mutable = True
        url = self.request.get_full_path()
        qd['next'] = url
        query_params = qd.urlencode()
        add_btn = '<a href="{}?{}" class="btn btn-info" style="margin: 11px 0">添加客户</a>'.format(
            reverse('crm:add_customer'), query_params)
        return add_btn, query_params


# --------------------------------------------------------------------------
# def add_customer(request):
#     form_obj = CustomerForm()
#     username = request.session.get('username')
#     if request.method == 'POST':
#         # 实例化一个带提交数据的form对象
#         form_obj = CustomerForm(request.POST)
#         # 对提交数据进行校验
#         if form_obj.is_valid():
#             # 创建对象
#             form_obj.save()
#             return redirect(reverse('crm:customer_list'))
#     return render(request, 'crm/add_customer.html', {'form_obj': form_obj, 'username': username})
#
#
# # 编辑客户
# def edit_customer(request, edit_id):
#     # 根据ID查出所需要编辑的客户对象
#     obj = Customer.objects.filter(id=edit_id).first()
#     form_obj = CustomerForm(instance=obj)
#     if request.method == 'POST':
#         # 将提交的数据和要修改的实例交给form对象
#         form_obj = CustomerForm(request.POST, instance=obj)
#         if form_obj.is_valid():
#             form_obj.save()
#             return redirect(reverse('customer'))
#     return render(request, 'crm/add_customer.html', {"form_obj": form_obj})


# 增加编辑一起
@login_required
def customer(request, edit_id=None):
    customer_obj = Customer.objects.filter(id=edit_id).first()
    form_obj = CustomerForm(instance=customer_obj)
    if request.method == 'POST':
        form_obj = CustomerForm(request.POST, instance=customer_obj)
        if form_obj.is_valid():
            form_obj.save()
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(reverse('crm:customer_list'))
    return render(request, 'crm/consult/customer.html', {'form_obj': form_obj, 'edit_id': edit_id})


# ----------------------------------------------------------------------------------------------------
# # 展示跟进状态
# def show_consult_record(request):
#     consult_record_obj = ConsultRecord.objects.filter(delete_status=False)
#     return render(request, 'crm/consult_record_list.html', {'all_consult_record': consult_record_obj})


# 展示跟进状态CBV模式
class ShowConsultRecord(LoginRequired):
    def get(self, request, customer_id):
        if customer_id == '0':
            consult_record_obj = ConsultRecord.objects.filter(delete_status=False)
        else:
            consult_record_obj = ConsultRecord.objects.filter(customer_id=customer_id, delete_status=False)
        page = Pagination(request, consult_record_obj.count(), per_num=4)
        return render(request, 'crm/consult/consult_record_list.html', {
            'all_consult_record': consult_record_obj[page.start:page.end],
            'pagination': page.show_li,
        })


#
# # 添加跟进状态
# def add_consult_record(request):
#     consult_record_obj = ConsultRecord(consultant=request.user)
#     consult_record_form = ConsultRecordForm(instance=consult_record_obj)
#     if request.method == 'POST':
#         consult_record_form = ConsultRecordForm(request.POST, instance=consult_record_obj)
#         if consult_record_form.is_valid():
#             consult_record_form.save()
#             return redirect(reverse('crm:consult_record'))
#     return render(request, 'crm/consult_record.html', {'form_obj': consult_record_form})
#
#
# # 编辑跟进状态
# def edit_consult_record(request, edit_id):
#     consult_record_obj = ConsultRecord.objects.filter(id=edit_id).first()
#     consult_record_form = ConsultRecordForm(instance=consult_record_obj)
#     if request.method == 'POST':
#         consult_record_form = ConsultRecordForm(request.POST, instance=consult_record_obj)
#         if consult_record_form.is_valid():
#             consult_record_form.save()
#             return redirect(reverse('crm:consult_record'))
#     return render(request, 'crm/consult_record.html', {'form_obj': consult_record_form})


# 新增和编辑跟进记录
def consult_record(request, edit_id=None):
    obj = ConsultRecord.objects.filter(id=edit_id).first() or ConsultRecord(consultant=request.user)
    form_obj = ConsultRecordForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultRecordForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('crm:consult_record', args=(0,)))

    return render(request, 'crm/consult/consult_record.html',
                  {'form_obj': form_obj, 'edit_id': edit_id})


# --------------------------------------------------------------------------------------------
class ShowEnrollment(LoginRequired):
    def get(self, request, customer_id):
        if customer_id == '0':
            all_record = Enrollment.objects.filter(delete_status=False, customer__consultant=request.user)
        else:
            all_record = Enrollment.objects.filter(customer_id=customer_id, delete_status=False)

            # 获取搜索条件
        query_params = self.get_query_params()
        page = Pagination(request, all_record.count(), per_num=4)
        return render(request, 'crm/consult/enrollment_list.html',
                      {
                          'all_record': all_record,
                          'query_params': query_params,
                          'pagination': page.show_li
                      })

    def get_query_params(self):
        url = self.request.get_full_path()
        qd = QueryDict()
        qd._mutable = True
        qd['next'] = url
        query_params = qd.urlencode()

        return query_params


# def add_enrollment(request, customer_id):
#     try:
#         enrollment_obj = Enrollment(customer_id=customer_id)
#         enrollment_form = EnrollmentForm(instance=enrollment_obj)
#         if request.method == 'POST':
#             enrollment_form = EnrollmentForm(request.POST, instance=enrollment_obj)
#             if enrollment_form.is_valid():
#                 enrollment_form.save()
#                 return redirect(reverse('crm:enrollment', args=(0,)))
#         return render(request, 'crm/enrollment.html', {'form_obj': enrollment_form})
#     except Exception as e:
#         print('----------->', e)


# 新增和编辑报名记录
def enrollment(request, customer_id=None, edit_id=None):
    obj = Enrollment.objects.filter(id=edit_id).first() or Enrollment(customer_id=customer_id)
    form_obj = EnrollmentForm(instance=obj)
    if request.method == 'POST':
        form_obj = EnrollmentForm(request.POST, instance=obj)
        if form_obj.is_valid():
            enrollment_obj = form_obj.save()
            # 修改客户的状态

            enrollment_obj.customer.status = 'signed'
            enrollment_obj.customer.save()

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect(reverse('crm:my_customer'))

    return render(request, 'crm/consult/enrollment.html',
                  {'form_obj': form_obj, 'edit_id': edit_id})
