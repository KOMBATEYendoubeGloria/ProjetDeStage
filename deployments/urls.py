from rest_framework.routers import DefaultRouter
from .views import DeploiementViewSet

router = DefaultRouter()
router.register('', DeploiementViewSet, basename='deploiement')

urlpatterns = router.urls