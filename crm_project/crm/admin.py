from django.contrib import admin
from crm import models
from rbac.models import Permission, Role, User, Menu
# Register your models here.

admin.site.register(models.Customer)
admin.site.register(models.ClassList)
admin.site.register(models.Campuses)


class PermissionAdmin(admin.ModelAdmin):
    """
    权限表在admin中的展示格式
    """
    list_display = ['title', 'url', 'name']
    list_editable = ['url', 'name']


admin.site.register(Permission, PermissionAdmin)
admin.site.register(Role)
admin.site.register(User)
admin.site.register(Menu)
