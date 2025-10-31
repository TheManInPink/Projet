# tests/test_dataverse_harvester.py
import pytest
from data_collector.harvesters import dataverse as dv_h

class DummyResp:
    def __init__(self, json_data, status=200):
        self._j, self.status_code = json_data, status
    def raise_for_status(self): pass
    def json(self): return self._j

def test_dataverse_search_parses_results(monkeypatch):
    def fake_get(url, params=None, timeout=None, headers=None):
        return DummyResp({
            "data": {
                "total_count": 1,
                "items": [{
                    "global_id": "doi:10.123/abc",
                    "name": "Hydro Dataset",
                    "description": "desc",
                    "keywords": ["hydro"],
                    "identifier_of_dataverse": "uqar",
                    "url": "https://borealisdata.ca/dataset/xyz",
                    "citation": "citation text",
                    "fileCount": 3,
                    "published_at": "2021-01-01T00:00:00Z",
                    "publication_date": "2021-01-02"
                }]
            }
        })
    monkeypatch.setattr(dv_h.requests, "get", fake_get)

    items = list(dv_h.search(subtree_alias='uqar', q="hydro"))
    assert len(items) == 1
    
    mapped = dv_h.to_dataset(items[0])
    assert mapped["external_id"].startswith("doi:")
    assert mapped["title"] == "Hydro Dataset"
