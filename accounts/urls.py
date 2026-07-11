from django.urls import path
from . import views

urlpatterns = [
    path('register/',                  views.register,           name='register'),
    path('login/',                     views.login_view,         name='login'),
    path('logout/',                    views.logout_view,        name='logout'),
    path('dashboard/',                 views.dashboard,          name='dashboard'),
    path('profile/',                   views.profile,            name='profile'),
    path('loyalty/',                   views.loyalty_dashboard,  name='loyalty_dashboard'),
    path('avon/',                      views.avon_dashboard,     name='avon_dashboard'),
    path('profile/<str:username>/',    views.public_profile,     name='public_profile'),

    # Security
    path('forgot-password/',                      views.forgot_password,  name='forgot_password'),
    path('reset-password/<str:token>/',           views.reset_password,   name='reset_password'),
    path('verify-email/<str:token>/',             views.verify_email,     name='verify_email'),
    path('set-withdrawal-pin/',                   views.set_withdrawal_pin, name='set_withdrawal_pin'),
]
