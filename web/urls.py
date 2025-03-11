from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TimezoneViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'timezones', TimezoneViewSet, basename='timezone')

urlpatterns = [path('', include(router.urls))]
