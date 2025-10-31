# api/views.py
from rest_framework import viewsets, filters
from data_collector.models import Dataset, DataSource, HarvestingLog
from .serializers import DatasetSerializer, DataSourceSerializer, HarvestingLogSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .permissions import IsStaffOrReadOnly


class DatasetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title','description','organization','keywords']
    ordering_fields = ['harvested_at','created_at_src','modified_at_src','title']


    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Recherche plein texte (title, description, organization, keywords)", type=openapi.TYPE_STRING),
        openapi.Parameter('ordering', openapi.IN_QUERY, description="Tri: harvested_at, created_at_src, modified_at_src, title", type=openapi.TYPE_STRING),
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class DataSourceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer


class HarvestingLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HarvestingLog.objects.all()
    serializer_class = HarvestingLogSerializer
