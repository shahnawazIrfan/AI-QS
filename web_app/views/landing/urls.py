from django.urls import path
from web_app.views.landing import views

urlpatterns = [
    path('', views.landingView.as_view(), name='landing'),
    path('contact/', views.contactView.as_view(), name='contact')
]