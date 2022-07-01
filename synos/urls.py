
from django.contrib import admin
from django.urls import path , include
from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('excel/', include('excelImport.urls')),
    path('core/', include('delivery.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
    path('account/',include('account.urls')), 
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
