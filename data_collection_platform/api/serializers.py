# api/serializers.py
from rest_framework import serializers
from data_collector.models import Dataset, DataSource, HarvestingLog


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = '__all__'


class DatasetSerializer(serializers.ModelSerializer):
    source = DataSourceSerializer(read_only=True)
    source_id = serializers.PrimaryKeyRelatedField(
        queryset=DataSource.objects.all(), write_only=True, source='source'
    )
    class Meta:
        model = Dataset
        fields = [
                    'id',
                    'source',
                    'source_id',
                    'external_id',
                    'title',
                    'description',
                    'keywords',
                    'organization',
                    'license',
                    'url',
                    'extras',
                    'created_at_src',
                    'modified_at_src',
                    'harvested_at'
                ]


class HarvestingLogSerializer(serializers.ModelSerializer):
    source = DataSourceSerializer(read_only=True)
    class Meta:
        model = HarvestingLog
        fields = '__all__'