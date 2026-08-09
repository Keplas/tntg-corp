from django.urls import path
from . import views

urlpatterns = [
    path('', views.training_home, name='training_home'),
    path('program/<int:pk>/', views.program_detail, name='program_detail'),
    path('program/<int:pk>/enroll/', views.enroll, name='enroll'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/reserve/', views.reserve_spot, name='reserve_spot'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
]
