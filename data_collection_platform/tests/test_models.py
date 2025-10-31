# tests/test_models.py
import pytest
from django.db import IntegrityError
from data_collector.models import DataSource, Dataset

@pytest.mark.django_db
def test_unique_dataset_per_source():
    src = DataSource.objects.create(name="OpenGouv", base_url="x", kind=DataSource.CKAN)
    Dataset.objects.create(source=src, external_id="abc", title="A")
    # La 2e insertion (même source/external_id) doit échouer
    with pytest.raises(IntegrityError):
        Dataset.objects.create(source=src, external_id="abc", title="B")
