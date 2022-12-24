"""root URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('root/', include('root.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from root.settings import STATIC_URL, STATIC_ROOT, MEDIA_URL, MEDIA_ROOT

admin.site.site_header = 'My project'  # default: "Django Administration"
admin.site.index_title = 'Features area'  # default: "Site administration"
admin.site.site_title = 'HTML title from adminsitration'


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('apps.urls')),
                  path('ckeditor/', include('ckeditor_uploader.urls')),
                  path('sentry-debug/', trigger_error),
                  path('accounts/', include('allauth.urls')),
              ] + static(STATIC_URL, document_root=STATIC_ROOT) + static(MEDIA_URL, document_root=MEDIA_ROOT)
