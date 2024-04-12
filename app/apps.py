from django import apps
from django.contrib.admin.apps import AdminConfig


class AppConfig(apps.AppConfig):
    name = 'app'
    verbose_name = 'App admin label'


class MyAdminConfig(AdminConfig):
    default_site = 'app.admin.my_admin_site.MyAdminSite'
