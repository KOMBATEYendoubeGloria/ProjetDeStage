from django.urls import include, path

from .views import DevopsHealthCheckView

urlpatterns = [
    path('', DevopsHealthCheckView.as_view(), name='devops-health'),
    path('api/', include('devops.api.urls')),
]
