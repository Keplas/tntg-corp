from django.urls import path
from . import views
from .chatbot import chatbot_api

urlpatterns = [
    path('withdrawals/<int:pk>/approve/', views.approve_withdrawal, name='approve_withdrawal'),
    path('withdrawals/<int:pk>/reject/',  views.reject_withdrawal,  name='reject_withdrawal'),
    path('',              views.home,                name='home'),
    path('about/',        views.about,               name='about'),
    path('contact/',      views.contact,             name='contact'),
    path('loyalty/',      views.loyalty_info,        name='loyalty_info'),
    # Legacy redirects — keep so old bookmarks / templates still resolve
    path('avon-points/',  views.loyalty_info,        name='avon_points_info'),
    path('coffee/',       views.coffee,              name='coffee'),
    path('notifications/', views.notifications,                      name='notifications'),
    path('notifications/mark-read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/',      views.mark_all_read,          name='mark_all_read'),
    path('notifications/count/',              views.notification_count,     name='notification_count'),
    path('chat/',         chatbot_api,               name='chatbot_api'),
    # SEO
    path('sitemap.xml',   views.sitemap_xml,         name='sitemap_xml'),
    path('robots.txt',    views.robots_txt,          name='robots_txt'),
    path('privacy-policy/',   views.privacy_policy,      name='privacy_policy'),
    path('faq/',               views.faq,                  name='faq'),
    path('newsletter/',        views.newsletter_subscribe, name='newsletter_subscribe'),
    path('terms/',            views.terms,               name='terms'),
    # Analytics (staff only)
    path('analytics/',    views.analytics_dashboard, name='analytics_dashboard'),
    # Language toggle
    path('set-language/', views.set_language,        name='set_language'),
    path('blog/',             views.blog_list,   name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
]
