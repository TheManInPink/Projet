# tests/test_api_graphql.py
import pytest, json
from django.urls import reverse
from data_collector.models import DataSource, Dataset

@pytest.mark.django_db
def test_api_list_datasets(client):
    src = DataSource.objects.create(name="OpenGouv", base_url="x", kind="CKAN")
    Dataset.objects.create(source=src, external_id="id1", title="Climate")

    # Si le nom de route te joue un tour, remplace par: resp = client.get("/api/datasets/")
    url = reverse("dataset-list")  # via DefaultRouter: basename 'dataset' si pas personnalisé
    resp = client.get(url)
    assert resp.status_code == 200
    body = resp.json()
    # assert resp.json()[0]["title"] == "Climate"
    assert isinstance(body, list) and body
    assert body[0]["title"] == "Climate"

@pytest.mark.django_db
def test_graphql_search(client):
    src = DataSource.objects.create(name="OpenGouv", base_url="x", kind="CKAN")
    Dataset.objects.create(source=src, external_id="id1", title="Climate")

    query = {'query': 'query{ searchDatasets(q:"clim"){ title } }'}
    # resp = client.post("/graphql", data={"query": 'query{ searchDatasets(q:"clim"){ title } }'})
    resp = client.post("/graphql", data=json.dumps(query), content_type="application/json")
    # Si 404 ici: vérifie que tu utilises GraphQLView.as_view(graphiql=True) sur /graphql
    assert resp.status_code == 200
    data = resp.json().get("data", {})
    assert data["searchDatasets"][0]["title"] == "Climate"


@pytest.mark.django_db
def test_graphql_datasets_with_filters(client):
    src = DataSource.objects.create(name="OpenGouv", base_url="x", kind="CKAN")
    Dataset.objects.create(source=src, external_id="id1", title="Climate A")
    q = {
        "query": "query($q:String,$limit:Int){ datasets(q:$q, limit:$limit){ title } }",
        "variables": {"q": "clim", "limit": 1},
    }
    resp = client.post("/graphql", data=json.dumps(q), content_type="application/json")
    assert resp.status_code == 200
    data = resp.json()["data"]["datasets"]
    assert len(data) == 1 and "Climate" in data[0]["title"]
