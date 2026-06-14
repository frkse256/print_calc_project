from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),

    path('printers/', views.printer_list, name='printer_list'),
    path('printers/create/', views.printer_create, name='printer_create'),

    path('filaments/', views.filament_list, name='filament_list'),
    path('filaments/create/', views.filament_create, name='filament_create'),

    path('jobs/', views.job_list, name='job_list'),
    path('jobs/create/', views.job_create, name='job_create'),

    path('analytics/', views.analytics, name='analytics'),
]