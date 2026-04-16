from django.urls import path
from . import views

urlpatterns = [
    path('', views.training_home, name='training_home'),
    path('program/<int:pk>/', views.program_detail, name='program_detail'),
    path('program/<int:pk>/enroll/', views.enroll, name='enroll'),
    path('tv/', views.tv_programs, name='tv_programs'),
]
