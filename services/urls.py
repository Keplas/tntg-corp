from django.urls import path
from . import views

urlpatterns = [
    path('', views.financial_services, name='financial_services'),
    path('insurance/', views.insurance, name='insurance'),
    path('brokerage/', views.brokerage, name='brokerage'),
    path('forex/', views.forex, name='forex'),
]
