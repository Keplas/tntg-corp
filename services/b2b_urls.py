"""
B2B Referral Platform URL patterns — included at path('b2b/', ...) in tntg_corp/urls.py.
"""
from django.urls import path
from . import b2b_views

urlpatterns = [
    path('',                        b2b_views.b2b_landing,         name='b2b_landing'),
    path('apply/',                  b2b_views.b2b_apply,           name='b2b_apply'),
    path('apply/success/',          b2b_views.b2b_apply_success,   name='b2b_apply_success'),
    path('portal/',                 b2b_views.b2b_portal,          name='b2b_portal'),
    path('my-applications/',        b2b_views.b2b_my_applications, name='b2b_my_applications'),
    path('ref/<str:code>/',         b2b_views.b2b_referral_track,  name='b2b_referral_track'),
]
