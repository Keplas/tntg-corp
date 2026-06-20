from django.urls import path
from . import views
from .chatbot import chatbot_api
from .views_image_upload import image_upload_page, image_upload_api, image_auto_match, product_thumb_url

urlpatterns = [
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
    # Bulk image upload (admin only)
    path('admin/upload-images/',              image_upload_page,  name='image_upload_page'),
    path('admin/upload-images/upload/',       image_upload_api,   name='image_upload_api'),
    path('admin/upload-images/match/',        image_auto_match,   name='image_auto_match'),
    path('admin/upload-images/thumb/<int:product_id>/', product_thumb_url, name='product_thumb_url'),
]
