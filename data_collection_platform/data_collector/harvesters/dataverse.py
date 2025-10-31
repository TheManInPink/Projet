# data_collector/harvesters/dataverse.py
from __future__ import annotations
from data_collector.http import session as http_session
from data_collector.utils import coerce_dt

# UQAR dataverse subtree
DATAVERSE_SEARCH = 'https://borealisdata.ca/api/search'
HEADERS = {"User-Agent": "OGSL-harvester/1.0"}
S = http_session()


def search(subtree_alias: str = 'uqar', q: str = '*', per_page: int = 100, max_pages: int = 5):
    params = {'q': q or '*', 'type': 'dataset', 'subtree': subtree_alias, 'per_page': per_page, 'start': 0}
    for _ in range(max_pages):
        r = S.get(DATAVERSE_SEARCH, params=params, headers=HEADERS)  # <<< S.get
        r.raise_for_status()
        data = r.json()
        items = (data.get('data') or {}).get('items', [])
        for it in items:
            yield it
        total = (data.get('data') or {}).get('total_count', 0)
        if params['start'] + params['per_page'] >= total:
            break
        params['start'] += params['per_page']

def to_dataset(item: dict) -> dict:
    # return {
    #     'external_id': item.get('global_id') or item.get('name'),
    #     'title': item.get('name') or '',
    #     'description': item.get('description') or '',
    #     'keywords': item.get('keywords') or [],
    #     'organization': (item.get('identifier_of_dataverse') or '').upper(),
    #     'license': '',
    #     'url': item.get('url') or '',
    #     'extras': {'citation': item.get('citation'), 'fileCount': item.get('fileCount')},
    #     'created_at_src': coerce_dt(item.get('published_at')),
    #     'modified_at_src': coerce_dt(item.get('publication_date')),
    # }

    def cut(s, n): return s[:n] if isinstance(s, str) else s
    return {
        'external_id': cut(item.get('global_id') or item.get('name') or '', 191),
        'title':       cut(item.get('name') or '', 500),
        'description': item.get('description') or '',
        'keywords':    item.get('keywords') or [],
        'organization': cut((item.get('identifier_of_dataverse') or '').upper(), 191),
        'license':     '',
        'url':         cut(item.get('url') or '', 2048),
        'extras': {'citation': item.get('citation'), 'fileCount': item.get('fileCount')},
        'created_at_src':  coerce_dt(item.get('published_at')),
        'modified_at_src': coerce_dt(item.get('publication_date')),
    }