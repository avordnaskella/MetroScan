from django.urls import path
from . import views

urlpatterns = [
    path('api/register_pass/', views.register_pass, name='register_pass'),
    path('', views.dashboard, name='dashboard'),
]