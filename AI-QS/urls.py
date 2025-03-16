from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path("", include("web_app.urls")),
]