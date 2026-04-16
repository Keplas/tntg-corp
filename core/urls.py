from django.urls import path
from . import views
from .chatbot import chatbot_api

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('coffee/', views.coffee, name='coffee'),
    path('avon-points/', views.avon_points_info, name='avon_points_info'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/count/', views.notification_count, name='notification_count'),
    path('chat/', chatbot_api, name='chatbot_api'),
]
