from rest_framework.routers import DefaultRouter
from .views import ProjetApplicatifViewSet

router = DefaultRouter()
router.register('', ProjetApplicatifViewSet, basename='projet')

urlpatterns = router.urls