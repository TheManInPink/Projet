# tests/test_ckan_harvester.py
import pytest
import types
from data_collector.harvesters import ckan as ckan_h

class DummyResp:
    def __init__(self, json_data, status=200): 
        self._j, self.status_code = json_data, status
    def raise_for_status(self): pass
    def json(self): return self._j

def test_ckan_search_parses_results(monkeypatch):
    def fake_get(url, params=None, timeout=None, headers=None):
        return DummyResp({
            "success": True,
            "result": {
                "count": 1,
                "results": [{
                    "id": "id1",
                    "title": "Climate Data",
                    "notes": "desc",
                    "tags": [{"display_name": "climate"}],
                    "organization": {"title": "Org"},
                    "license_title": "Open",
                    "resources": [],
                    "metadata_created": "2020-01-01T00:00:00",
                    "metadata_modified": "2020-01-02T00:00:00"
                }]
            }
        })
    
    # Remplace requests.get par notre fake
    monkeypatch.setattr(ckan_h.requests, "get", fake_get)

    base = "https://example/api/3/action"
    results = list(ckan_h.search(base_url=base, q="climate"))
    assert len(results) == 1

    mapped = ckan_h._ckan_to_dataset(results[0])
    assert mapped["title"] == "Climate Data"
    assert mapped["external_id"] == "id1"
