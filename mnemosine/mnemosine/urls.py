from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')), # Inclui as URLs do app dashboard
    path('edital/', include('edital.urls')), # Inclui as URLs do app dashboard
]
