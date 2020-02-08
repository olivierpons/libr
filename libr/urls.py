from django.urls import path, re_path
from django.views import static

from app.admin.base import my_admin_site
from libr import settings

urlpatterns = [
    path('admin/', my_admin_site.urls),
    re_path(r'^public/(?P<path>.*)$', static.serve, {
        'document_root': settings.MEDIA_ROOT
    }, name='url_public'),
]
