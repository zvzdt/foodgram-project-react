from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('api/', include('rest_framework.urls')),
    path('api/', include('api.urls')),
]
