"""crm_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from crm.views import index

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', index.index, name='index'),
    url(r'^login/', index.login, name='login'),
    url(r'^v_code/', index.v_code, name='v_code'),
    url(r'^register/', index.register, name='register'),
    url(r'^crm/', include('crm.urls', namespace='crm')),
    url(r'^rbac/', include('rbac.urls', namespace='rbac')),
]
