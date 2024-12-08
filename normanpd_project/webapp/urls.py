from django.urls import path
from webapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.upload_files, name='upload_files'),
    path('process/', views.process_files, name='process_files'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)