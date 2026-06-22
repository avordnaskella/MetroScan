from django.urls import path
from . import views

urlpatterns = [
    path('api/register_pass/', views.register_pass, name='register_pass'),
    path('', views.dashboard, name='dashboard'),
    path('export/csv/', views.export_csv, name='export_csv'), 
]