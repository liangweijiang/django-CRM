from django.db import models


# Create your models here.
class Menu(models.Model):
    """
    一级菜单
    """
    title = models.CharField(max_length=32, verbose_name='标题')
    icon = models.CharField(max_length=64, verbose_name='图标', null=True, blank=True)
    weight = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '菜单'
        verbose_name_plural = '菜单'


class Permission(models.Model):
    """
    权限表
    """
    title = models.CharField(max_length=32, verbose_name='标题')
    url = models.CharField(max_length=128, verbose_name='权限')
    menu = models.ForeignKey(to='Menu', null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    name = models.CharField(max_length=32, null=True, blank=True, unique=True)
    # is_menu = models.BooleanField(default=False, verbose_name='是否是菜单')
    # icon = models.CharField(max_length=32, verbose_name='图标', null=True, blank=True)

    class Meta:
        verbose_name_plural = '权限表'
        verbose_name = '权限表'

    def __str__(self):
        return self.title


class Role(models.Model):
    """
    角色表
    """
    name = models.CharField(max_length=32, verbose_name='角色名称')
    permissions = models.ManyToManyField(to='Permission', verbose_name='角色拥有的权限', blank=True)

    class Meta:
        verbose_name_plural = '角色表'
        verbose_name = '角色表'

    def __str__(self):
        return self.name


class User(models.Model):
    """
    用户表
    """
    username = models.CharField(max_length=32, verbose_name='用户名')
    password = models.CharField(max_length=32, verbose_name='密码')
    roles = models.ManyToManyField(to='Role', verbose_name='用户所拥有的身份', blank=True)

    class Meta:
        verbose_name_plural = '用户表'
        verbose_name = '用户表'

    def __str__(self):
        return self.username
