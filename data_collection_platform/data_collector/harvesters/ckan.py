# data_collector/harvesters/ckan.py
from __future__ import annotations

from data_collector.http import session as http_session
from data_collector.utils import coerce_dt

HEADERS = {"User-Agent": "OGSL-harvester/1.0"}

S = http_session()  # <<< session avec retries

CKAN_BASES = {
    # Note: /data/en/api/… pour OpenGouv; /data/api/… pour CanWin
    "OpenGouv":      "https://open.canada.ca/data/en/api/3/action",
    "CanWin":        "https://canwin-datahub.ad.umanitoba.ca/data/api/3/action",
    "DonneesQuebec": "https://www.donneesquebec.ca/recherche/api/3/action",
}

__all__ = ['search', '_ckan_to_dataset', 'CKAN_BASES']


# fields mapping helper
def _ckan_to_dataset(pkg: dict) -> dict:
    def cut(s, n): return s[:n] if isinstance(s, str) else s
    org = (pkg.get('organization') or {}).get('title', '')
    # normalise les tags (unicité + trim + ordre stable)
    raw_tags = [(t.get('display_name') or t.get('name') or '').strip() for t in pkg.get('tags', [])]
    tags = sorted({t for t in raw_tags if t}, key=str.lower)
    lic = pkg.get('license_title') or pkg.get('license_id') or ''
    url = pkg.get('url') or pkg.get('ckan_url') or ''
    
    return {
    #    'external_id': pkg.get('id'),
        'external_id': cut(pkg.get('id') or '', 191),
        # 'title': (pkg.get('title') or pkg.get('name') or '').strip(),
        'title':         cut((pkg.get('title') or pkg.get('name') or '').strip(), 500),
        'description': pkg.get('notes') or '',
        'keywords': tags,
        # 'organization': org or '',
        # 'license': lic,
        # 'url': url,
        'organization':  cut(org or '', 191),
        'license':       cut(lic or '', 255),
        'url':           cut(url, 2048),
        'extras': {
            'resources': pkg.get('resources', []),
            'metadata_created': pkg.get('metadata_created'),
        },
        'created_at_src': coerce_dt(pkg.get('metadata_created')),
        'modified_at_src': coerce_dt(pkg.get('metadata_modified')),
    }

def _page(base_url: str, params: dict):
    r = S.get(f"{base_url}/package_search", params=params, headers=HEADERS)  # <<< S.get
    r.raise_for_status()
    j = r.json()
    if not j.get("success", True):
        return 0, []
    res = j.get("result", {})
    return res.get("count", 0), res.get("results", [])


def search(base_url: str, q: str = '', filters: dict | None = None, rows: int = 100, max_pages: int = 5):
    # 1) première passe: q tel quel (ou *:*)
    params = {'q': q or '*:*', 'rows': rows, 'start': 0}
    if filters:
        fq = ' '.join(f"{k}:{v}" for k, v in filters.items() if v)
        if fq:
            params['fq'] = fq

    total_seen = 0
    for _ in range(max_pages):
        count, results = _page(base_url, params)
        if results:
            for pkg in results:
                yield pkg
            total_seen += len(results)
            if total_seen >= count:
                break
            params['start'] += rows
        else:
            break

    # 2) fallback si rien trouvé et q non vide: élargir la requête
    if q and total_seen == 0:
        params = {
            'q': f"title:{q} OR notes:{q} OR tags:{q}",
            'rows': rows,
            'start': 0
        }
        for _ in range(max_pages):
            count, results = _page(base_url, params)
            if results:
                for pkg in results:
                    yield pkg
                total_seen += len(results)
                if total_seen >= count:
                    break
                params['start'] += rows
            else:
                break