from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.pro_home,         name='pro_home'),
    path('<slug:slug>/',        views.pro_department,   name='pro_department'),
    path('book/<int:pkg_id>/',  views.pro_book,         name='pro_book'),
    path('confirmed/<int:pk>/', views.pro_confirmation, name='pro_confirmation'),
]
