# api/schema.py
import graphene
from graphene_django import DjangoObjectType
from data_collector.models import Dataset, DataSource, HarvestingLog


class DataSourceType(DjangoObjectType):
    class Meta:
        model = DataSource
        fields = '__all__'


class DatasetType(DjangoObjectType):
    class Meta:
        model = Dataset
        fields = '__all__'


class HarvestingLogType(DjangoObjectType):
    class Meta:
        model = HarvestingLog
        fields = '__all__'


class Query(graphene.ObjectType):
    all_datasets = graphene.List(DatasetType)
    dataset_by_id = graphene.Field(DatasetType, id=graphene.Int(required=True))
    datasets_by_source = graphene.List(DatasetType, source_name=graphene.String(required=True))
    search_datasets = graphene.List(DatasetType, q=graphene.String(required=True))


    def resolve_all_datasets(root, info):
        return Dataset.objects.all()


    def resolve_dataset_by_id(root, info, id):
        return Dataset.objects.filter(id=id).first()


    def resolve_datasets_by_source(root, info, source_name):
        return Dataset.objects.filter(source__name__iexact=source_name)


    def resolve_search_datasets(root, info, q):
        return Dataset.objects.filter(title__icontains=q) | Dataset.objects.filter(description__icontains=q)


schema = graphene.Schema(query=Query)