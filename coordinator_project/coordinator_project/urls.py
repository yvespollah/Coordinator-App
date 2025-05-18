from django.contrib import admin
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('manager.urls')),
    path('api/', include('volunteer.urls')),
    path('api/', include('communication.urls')),
]
