from django.urls import path, re_path
from django.views import static

from app.admin.base import my_admin_site
from app.views.index import IndexView
from app.views.login import LibrLoginView
from app.views.logout import LogoutView
from app.views.profile import ProfileView
from app.views.register import RegisterView
from libr import settings

urlpatterns = [
    path('admin/', my_admin_site.urls),
    re_path(r'^public/(?P<path>.*)$', static.serve, {
        'document_root': settings.MEDIA_ROOT
    }, name='url_public'),
    path('login', LibrLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('register', RegisterView.as_view(), name='register'),
    path('register-success', IndexView.as_view(), name='register_success'),
]
