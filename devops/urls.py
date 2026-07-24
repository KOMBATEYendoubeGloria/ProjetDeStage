from django.urls import path
from .views import DevopsHealthCheckView

urlpatterns = [
    path('', DevopsHealthCheckView.as_view(), name='devops-health'),
]
