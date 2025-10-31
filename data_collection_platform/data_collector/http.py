# data_collector/http.py
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def _wrap_timeout(request_func, timeout):
    def wrapped(method, url, **kwargs):
        kwargs.setdefault("timeout", timeout)
        return request_func(method, url, **kwargs)
    return wrapped

def session(user_agent="OGSL-harvester/1.0", timeout=60):
    s = requests.Session()
    s.headers.update({"User-Agent": user_agent})
    retry = Retry(
        total=4,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "POST"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.request = _wrap_timeout(s.request, timeout)
    return s
# data_collector/http.py
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def _wrap_timeout(request_func, timeout):
    def wrapped(method, url, **kwargs):
        kwargs.setdefault("timeout", timeout)
        return request_func(method, url, **kwargs)
    return wrapped

def session(user_agent="OGSL-harvester/1.0", timeout=60):
    s = requests.Session()
    s.headers.update({"User-Agent": user_agent})
    retry = Retry(
        total=4,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "POST"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.request = _wrap_timeout(s.request, timeout)
    return s
