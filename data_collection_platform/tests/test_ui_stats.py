# tests/test_ui_stats.py
import pytest
from data_collector.models import DataSource, Dataset

@pytest.mark.django_db
def test_stats_page_renders(client):
    src = DataSource.objects.create(name='OpenGouv', base_url='x', kind='CKAN')
    Dataset.objects.create(source=src, external_id='id1', title='A', keywords=['climate'])
    resp = client.get('/stats/')
    assert resp.status_code == 200
    assert b'chartBySource' in resp.content
