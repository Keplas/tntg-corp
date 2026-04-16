from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('accounts/', include('accounts.urls')),
    path('services/', include('services.urls')),
    path('training/', include('training.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
