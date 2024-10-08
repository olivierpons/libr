from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, re_path
from django.views import static
from django.views.i18n import JavaScriptCatalog

from app.admin.base import my_admin_site
from app.views.index import HomeView
from app.views.json.text_detect.by_coordinates import \
    TextDetectByCoordinatesView
from app.views.json.text_detect.by_upload import TextDetectByUploadView
from app.views.login import LibrLoginView
from app.views.logout import LogoutView
from app.views.profile import ProfileView
from app.views.register import RegisterView

urlpatterns = [
    path('admin/', my_admin_site.urls),
    re_path(r'^public/(?P<path>.*)$', static.serve, {
        'document_root': settings.MEDIA_ROOT
    }, name='url_public'),
    path('login', LibrLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('register', RegisterView.as_view(), name='register'),
    path('register-success', HomeView.as_view(), name='register_success'),
    path('j/text-detect-by-coordinates', TextDetectByCoordinatesView.as_view(),
         name='text_detect_by_coordinates'),
    path('j/text-detect-by-upload', TextDetectByUploadView.as_view(),
         name='text_detect_by_upload'),
]


urlpatterns += i18n_patterns(
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('', HomeView.as_view(), name='app_home'),
)
