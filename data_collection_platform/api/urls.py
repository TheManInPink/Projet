# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DatasetViewSet, DataSourceViewSet, HarvestingLogViewSet


router = DefaultRouter()
router.register(r'datasets', DatasetViewSet)
router.register(r'sources', DataSourceViewSet)
router.register(r'harvest-logs', HarvestingLogViewSet)


urlpatterns = [
    path('', include(router.urls)),         
]