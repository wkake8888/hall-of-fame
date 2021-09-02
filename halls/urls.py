from rest_framework import routers
from .views import VideoUserRelationViewSet

app_name = 'halls'
router = routers.DefaultRouter()
router.register(r'likes', VideoUserRelationViewSet)

urlpatterns = router.urls
