# ui/views.py
from django.shortcuts import render
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
from django.views.decorators.cache import cache_page
from collections import Counter
from data_collector.models import Dataset, DataSource, HarvestingLog

def index(request):
    q = request.GET.get('q','').strip()
    qs = Dataset.objects.all()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(organization__icontains=q)
        )
    return render(request, 'ui/index.html', { 'q': q, 'datasets': qs[:100] })

@cache_page(60 * 5)  # cache 5 minutes
def stats(request):
    # 1) Jeux par source
    per_source = list(
        Dataset.objects.values('source__name')
        .annotate(n=Count('id'))
        .order_by('-n')
    )
    source_labels = [row['source__name'] or '—' for row in per_source]
    source_values = [row['n'] for row in per_source]

    # 2) Tendances mensuelles (selon harvested_at)
    trend_qs = (
        Dataset.objects
        .annotate(month=TruncMonth('harvested_at'))
        .values('month')
        .annotate(n=Count('id'))
        .order_by('month')
    )
    trend_labels = [row['month'].strftime('%Y-%m') if row['month'] else 'N/A' for row in trend_qs]
    trend_values = [row['n'] for row in trend_qs]

    # 3) Top mots-clés (sur un échantillon récent)
    recent_kw = Dataset.objects.order_by('-harvested_at').values_list('keywords', flat=True)[:5000]
    counter = Counter()
    for arr in recent_kw:
        if isinstance(arr, list):
            for kw in arr:
                k = (str(kw) if kw is not None else '').strip()
                if k:
                    counter[k] += 1
    top_kw = counter.most_common(10)
    kw_labels = [k for (k, _) in top_kw]
    kw_values = [v for (_, v) in top_kw]

    # 4) Statuts des moissons
    logs_status = list(
        HarvestingLog.objects.values('status')
        .annotate(n=Count('id'))
        .order_by('-n')
    )
    status_labels = [row['status'] for row in logs_status]
    status_values = [row['n'] for row in logs_status]

    # 5) KPI & top organisations
    total_datasets = Dataset.objects.count()
    total_sources = DataSource.objects.count()
    total_logs = HarvestingLog.objects.count()
    top_orgs = list(
        Dataset.objects.values('organization')
        .annotate(n=Count('id'))
        .order_by('-n')[:10]
    )

    ctx = {
        'source_labels': source_labels,
        'source_values': source_values,
        'trend_labels': trend_labels,
        'trend_values': trend_values,
        'kw_labels': kw_labels,
        'kw_values': kw_values,
        'status_labels': status_labels,
        'status_values': status_values,
        'total_datasets': total_datasets,
        'total_sources': total_sources,
        'total_logs': total_logs,
        'top_orgs': top_orgs,
    }
    return render(request, 'ui/stats.html', ctx)