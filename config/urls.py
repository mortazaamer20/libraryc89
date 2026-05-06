from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from api.reports.admin_views import library_reports_view


urlpatterns = [
    path("admin/reports/", admin.site.admin_view(library_reports_view), name="library-reports"),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
     
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)