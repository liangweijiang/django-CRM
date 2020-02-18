from django.shortcuts import render, redirect, reverse, HttpResponse
from rbac.models import Role, Menu, Permission, User
from rbac.forms import RoleForm, MenuForm, PermissionForm, MultiPermissionForm
from django.db.models import Q
from rbac.server.routes import get_all_url_dict


# Create your views here.


def role_list(request):
    all_roles = Role.objects.all()
    return render(request, 'rbac/role_list.html', {'role_list': all_roles})


def role(request, rid=None):
    role_obj = Role.objects.filter(id=rid).first()
    form_obj = RoleForm(instance=role_obj)
    if request.method == 'POST':
        form_obj = RoleForm(request.POST, instance=role_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('rbac:role_list'))
    return render(request, 'rbac/role.html', {'form': form_obj})


def role_del(request, rid):
    Role.objects.filter(id=rid).delete()
    return redirect(reverse('rbac:role_list'))


# ---------------------------------------------------------------------------

def menu_list(request):
    all_menus = Menu.objects.all()
    mid = request.GET.get('mid')
    if mid:
        permission_query = Permission.objects.filter(Q(menu_id=mid) | Q(parent__menu_id=mid))
    else:
        permission_query = Permission.objects.all()
    all_permissions = permission_query.values('id', 'url', 'title', 'name', 'menu_id', 'parent_id', 'menu__title')
    all_permissions_dict = {}
    for item in all_permissions:
        menu_id = item.get('menu_id')
        if menu_id:
            item['children'] = []
            all_permissions_dict[item['id']] = item
    for item in all_permissions:
        pid = item.get('parent_id')
        if pid:
            all_permissions_dict[pid]['children'].append(item)
    return render(request, 'rbac/menu_list.html', {
        'menu_list': all_menus,
        'permission_dict': all_permissions_dict
    })


def menu(request, mid=None):
    menu_obj = Menu.objects.filter(id=mid).first()
    form_obj = MenuForm(instance=menu_obj)
    if request.method == 'POST':
        form_obj = MenuForm(request.POST, instance=menu_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('rbac:menu_list'))
    return render(request, 'rbac/form.html', {'form_obj': form_obj})


def menu_del(request, mid):
    Menu.objects.filter(id=mid).delete()
    return redirect(reverse('rbac:menu_list'))


# -------------------------------------------------------------------------------
def permission(request, edit_id=None):
    permission_obj = Permission.objects.filter(id=edit_id).first()
    form_obj = PermissionForm(instance=permission_obj)
    if request.method == 'POST':
        form_obj = PermissionForm(request.POST, instance=permission_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('rbac:menu_list'))
    return render(request, 'rbac/form.html', {'form_obj': form_obj})


def permission_del(request, del_id):
    Permission.objects.filter(id=del_id).delete()
    return redirect(reverse('rbac:menu_list'))


# --------------------------------------------------------------------------------------
from django.forms import modelformset_factory, formset_factory


def multi_permissions(request):
    """
    批量操作权限
    :param request:
    :return:
    """

    post_type = request.GET.get('type')

    # 更新和编辑用的
    FormSet = modelformset_factory(Permission, MultiPermissionForm, extra=0)
    # 增加用的
    AddFormSet = formset_factory(MultiPermissionForm, extra=0)

    permissions = Permission.objects.all()

    # 获取路由系统中所有URL
    router_dict = get_all_url_dict(ignore_namespace_list=['admin'])

    # 数据库中的所有权限的别名
    permissions_name_set = set([i.name for i in permissions])

    # 路由系统中的所有权限的别名
    router_name_set = set(router_dict.keys())
    add_name_set = router_name_set - permissions_name_set
    add_formset = AddFormSet(initial=[row for name, row in router_dict.items() if name in add_name_set])
    if request.method == 'POST' and post_type == 'add':
        add_formset = AddFormSet(request.POST)
        if add_formset.is_valid():
            print(add_formset.cleaned_data)
            permission_obj_list = [Permission(**i) for i in add_formset.cleaned_data]

            query_list = Permission.objects.bulk_create(permission_obj_list)

            for i in query_list:
                permissions_name_set.add(i.name)
            add_formset = AddFormSet()
        else:
            print(add_formset.errors)

    del_name_set = permissions_name_set - router_name_set
    del_formset = FormSet(queryset=Permission.objects.filter(name__in=del_name_set))

    update_name_set = permissions_name_set & router_name_set
    update_formset = FormSet(queryset=Permission.objects.filter(name__in=update_name_set))

    if request.method == 'POST' and post_type == 'update':
        update_formset = FormSet(request.POST)
        if update_formset.is_valid():
            update_formset.save()
            update_formset = FormSet(queryset=Permission.objects.filter(name__in=update_name_set))

    return render(
        request,
        'rbac/multi_permissions.html',
        {
            'del_formset': del_formset,
            'update_formset': update_formset,
            'add_formset': add_formset,
        }
    )


def distribute_permissions(request):
    """
    分配权限
    :param request:
    :return:
    """
    uid = request.GET.get('uid')
    rid = request.GET.get('rid')

    if request.method == 'POST' and request.POST.get('postType') == 'role':
        user = User.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        user.roles.set(request.POST.getlist('roles'))

    if request.method == 'POST' and request.POST.get('postType') == 'permission' and rid:
        role = Role.objects.filter(id=rid).first()
        if not role:
            return HttpResponse('角色不存在')
        role.permissions.set(request.POST.getlist('permissions'))

    # 所有用户
    user_list = User.objects.all()

    user_has_roles = User.objects.filter(id=uid).values('id', 'roles')

    # print(user_has_roles)

    user_has_roles_dict = {item['roles']: None for item in user_has_roles}

    """
    用户拥有的角色id
    user_has_roles_dict = { 角色id：None }
    """

    role_list = Role.objects.all()

    if rid:
        role_has_permissions = Role.objects.filter(id=rid).values('id', 'permissions')
    elif uid and not rid:
        # 没有rid则代表是点击了用户信息
        user = User.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        role_has_permissions = user.roles.values('id', 'permissions')
    else:
        role_has_permissions = []

    # print(role_has_permissions)

    role_has_permissions_dict = {item['permissions']: None for item in role_has_permissions}

    """
    角色拥有的权限id
    role_has_permissions_dict = { 权限id：None }
    """

    all_menu_list = []

    queryset = Menu.objects.values('id', 'title')
    menu_dict = {}

    """

    all_menu_list = [
            {  id:   title :  , children : [
                { 'id', 'title', 'menu_id', 'children: [
                'id', 'title', 'parent_id'
                ]  }
            ] },
            {'id': None, 'title': '其他', 'children': [
            {'id', 'title', 'parent_id'}]}
    ]

    menu_dict = {
        菜单的ID： {  id:   title :  , children : [
            { 'id', 'title', 'menu_id', 'children: [
            'id', 'title', 'parent_id'
            ]  }
        ] },
        none:{'id': None, 'title': '其他', 'children': [
        {'id', 'title', 'parent_id'}]}
    }
    """

    for item in queryset:
        item['children'] = []  # 放二级菜单，父权限
        menu_dict[item['id']] = item
        all_menu_list.append(item)

    other = {'id': None, 'title': '其他', 'children': []}
    all_menu_list.append(other)
    menu_dict[None] = other

    root_permission = Permission.objects.filter(menu__isnull=False).values('id', 'title', 'menu_id')

    root_permission_dict = {}

    """
    root_permission_dict = { 父权限的id ： { 'id', 'title', 'menu_id', 'children: [
        { 'id', 'title', 'parent_id' }
    ]  }}
    """

    for per in root_permission:
        per['children'] = []  # 放子权限
        nid = per['id']
        menu_id = per['menu_id']
        root_permission_dict[nid] = per
        menu_dict[menu_id]['children'].append(per)

    node_permission = Permission.objects.filter(menu__isnull=True).values('id', 'title', 'parent_id')

    for per in node_permission:
        pid = per['parent_id']
        if not pid:
            menu_dict[None]['children'].append(per)
            continue
        root_permission_dict[pid]['children'].append(per)
    print(user_has_roles_dict, role_has_permissions_dict)
    return render(
        request,
        'rbac/distribute_permissions.html',
        {
            'user_list': user_list,
            'role_list': role_list,
            'user_has_roles_dict': user_has_roles_dict,
            'role_has_permissions_dict': role_has_permissions_dict,
            'all_menu_list': all_menu_list,
            'uid': uid,
            'rid': rid
        }
    )
