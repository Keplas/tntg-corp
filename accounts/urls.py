from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('avon/', views.avon_dashboard, name='avon_dashboard'),
    path('profile/<str:username>/', views.public_profile, name='public_profile'),
]
