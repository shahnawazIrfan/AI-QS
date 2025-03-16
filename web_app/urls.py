from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [

    # Website landing Url
    path('', include('web_app.views.landing.urls')),
    
    # Portal Url
    path("dashboard/", include("web_app.views.dashboard.urls")),

    # Auth Urls
    path('auth/login/', auth_views.LoginView.as_view(template_name='login.html', extra_context={'hide_title': True}), name='login_url'),
    path('auth/logout/', auth_views.LogoutView.as_view(template_name='logout.html', extra_context={'hide_title': True}), name='logout_url')
]