from rest_framework import routers
from .views import VideoUserRelationViewSet

router = routers.DefaultRouter()
router.register(r'likes', VideoUserRelationViewSet)

urlpatterns = router.urls
