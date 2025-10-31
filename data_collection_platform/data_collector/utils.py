# data_collector/utils.py
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from datetime import timezone as dt_tz

def coerce_dt(value):
    """Convertit '2021-01-01T00:00:00Z' ou '2021-01-01' → datetime aware (UTC)."""
    if not value:
        return None
    if isinstance(value, str):
        dt = parse_datetime(value)
        if not dt and value.endswith('Z'):
            dt = parse_datetime(value.replace('Z', '+00:00'))
    else:
        dt = value
    if not dt:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, dt_tz.utc)
    return dt.astimezone(dt_tz.utc)
