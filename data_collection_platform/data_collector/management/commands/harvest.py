# data_collector/management/commands/harvest.py
from django.core.management.base import BaseCommand, CommandError
from data_collector.models import DataSource, Dataset, HarvestingLog
from data_collector.harvesters import ckan as ckan_h, dataverse as dv_h

from django.utils import timezone
from data_collector.utils import coerce_dt  # <<<


class Command(BaseCommand):
    help = "Moissonner des jeux de données depuis CKAN/Dataverse."

    def add_arguments(self, parser):
        parser.add_argument('--source', required=True,
                            choices=['OpenGouv','CanWin','DonneesQuebec','Borealis'])
        parser.add_argument('--q', default='')
        parser.add_argument('--max', type=int, default=500)
        parser.add_argument('--rows', type=int, default=100)
        parser.add_argument('--max-pages', type=int, default=5)
        parser.add_argument('--since', default=None, help="ISO datetime; ignore les entrées plus anciennes")  # <<<
        parser.add_argument('--incremental', action='store_true', help="Utilise DataSource.last_modified_cursor")  # <<<

    def handle(self, *args, **opts):
        source_name = opts['source']
        q = opts['q']
        rows = opts['rows']
        max_pages = opts['max_pages']

        since_dt = coerce_dt(opts.get('since')) if opts.get('since') else None  # <<<
        log = HarvestingLog.objects.create(query=q, status=HarvestingLog.PENDING)
        ds = None
        count = 0
        max_seen = since_dt  # <<<

        try:
            if source_name == 'Borealis':
                ds, _ = DataSource.objects.get_or_create(
                    name='Borealis',
                    defaults={'base_url': 'https://borealisdata.ca', 'kind': DataSource.DATAVERSE}
                )
                log.source = ds
                if opts.get('incremental') and ds.last_modified_cursor and not since_dt:  # <<<
                    since_dt = ds.last_modified_cursor

                for item in dv_h.search(subtree_alias='uqar', q=q, per_page=rows, max_pages=max_pages):
                    data = dv_h.to_dataset(item)
                    mod = data.get('modified_at_src') or data.get('created_at_src')  # <<<
                    if since_dt and mod and mod <= since_dt:
                        continue
                    Dataset.objects.update_or_create(
                        source=ds, external_id=data['external_id'], defaults=data
                    )
                    if mod and (max_seen is None or mod > max_seen):  # <<<
                        max_seen = mod
                    count += 1
                    if count >= opts['max']:
                        break

            elif source_name in ckan_h.CKAN_BASES:
                base = ckan_h.CKAN_BASES[source_name]
                ds, _ = DataSource.objects.get_or_create(
                    name=source_name, defaults={'base_url': base, 'kind': DataSource.CKAN}
                )
                log.source = ds
                if opts.get('incremental') and ds.last_modified_cursor and not since_dt:  # <<<
                    since_dt = ds.last_modified_cursor

                for pkg in ckan_h.search(base_url=base, q=q, rows=rows, max_pages=max_pages):
                    data = ckan_h._ckan_to_dataset(pkg)
                    mod = data.get('modified_at_src') or data.get('created_at_src')  # <<<
                    if since_dt and mod and mod <= since_dt:
                        continue
                    Dataset.objects.update_or_create(
                        source=ds, external_id=data['external_id'], defaults=data
                    )
                    if mod and (max_seen is None or mod > max_seen):  # <<<
                        max_seen = mod
                    count += 1
                    if count >= opts['max']:
                        break
            else:
                raise CommandError(f"Unknown source: {source_name}")

            # MàJ du curseur et du log
            if max_seen:
                ds.last_modified_cursor = max_seen  # <<<
            ds.last_success_at = timezone.now()      # <<<
            ds.save(update_fields=['last_modified_cursor','last_success_at'])

            log.items_found = count
            log.status = HarvestingLog.OK
            log.message = f"Harvested {count} items from {source_name} (q='{q}')"
            log.payload = {
                'since': since_dt.isoformat() if since_dt else None,
                'max_seen_modified': max_seen.isoformat() if max_seen else None
            }
            log.save()
            self.stdout.write(self.style.SUCCESS(log.message))

        except Exception as e:
            log.status = HarvestingLog.ERROR
            if ds:
                log.source = ds
            log.message = str(e)
            log.save()
            raise CommandError(f"Harvest error: {e}")