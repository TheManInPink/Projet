
from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils import timezone
from django.core.management import call_command
from .models import DataSource, Dataset, HarvestingLog, HarvestJob
import io, json

admin.site.site_header = "OGSL — Administration"
admin.site.index_title = "Gestion des catalogues & moissons"
admin.site.site_title = "OGSL Admin"

@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "base_url", "last_success_at", "last_modified_cursor")
    list_filter = ("kind",)
    search_fields = ("name", "base_url")
    readonly_fields = ("last_success_at", "last_modified_cursor")
    fieldsets = (
        (None, {"fields": ("name", "kind", "base_url")}),
        ("Suivi", {"fields": ("last_success_at", "last_modified_cursor"), "classes": ("collapse",)}),
        ("Notes", {"fields": ("notes",)}),
    )

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "organization", "modified_at_src", "harvested_at", "ext_link")
    list_filter = ("source__name",)
    search_fields = ("title", "description", "organization", "external_id")
    date_hierarchy = "harvested_at"
    autocomplete_fields = ("source",)
    readonly_fields = ("harvested_at", "extras_pretty")
    fields = (
        "source","external_id","title","description","keywords","organization","license","url",
        "extras_pretty","created_at_src","modified_at_src","harvested_at"
    )

    def ext_link(self, obj):
        return format_html('<a href="{}" target="_blank" title="Ouvrir"><i class="fa fa-link"></i></a>', obj.url) if obj.url else "-"
    ext_link.short_description = "Lien"

    def extras_pretty(self, obj):
        try:
            return format_html("<pre>{}</pre>", json.dumps(obj.extras, ensure_ascii=False, indent=2))
        except Exception:
            return obj.extras
    extras_pretty.short_description = "Extras (JSON)"

@admin.register(HarvestingLog)
class HarvestingLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "source", "status", "items_found", "message_short")
    list_filter = ("status", "source__name")
    search_fields = ("message", "query")
    readonly_fields = ("created_at",)

    def message_short(self, obj):
        return (obj.message or "")[:120]
    message_short.short_description = "Message"

@admin.action(description="▶️ Lancer maintenant")
def run_harvest_now(modeladmin, request, queryset):
    ok = ko = 0
    for job in queryset:
        out = io.StringIO()
        try:
            args = {
                'source': job.source.name,
                'q': job.query or '',
                'rows': job.rows,
                'max_pages': job.max_pages,
                'max': job.max_items,
            }
            if job.since:
                args['since'] = job.since.isoformat()
            if job.incremental:
                args['incremental'] = True

            call_command('harvest', stdout=out, **args)
            job.last_status = 'OK'
            job.last_message = out.getvalue()[-1000:]
            job.last_run = timezone.now()
            job.save(update_fields=["last_status", "last_message", "last_run"])
            ok += 1
        except Exception as e:
            job.last_status = 'ERROR'
            job.last_message = str(e)[:1000]
            job.last_run = timezone.now()
            job.save(update_fields=["last_status", "last_message", "last_run"])
            ko += 1
    if ok: messages.success(request, f"{ok} job(s) exécuté(s)")
    if ko: messages.error(request, f"{ko} échec(s) — voir 'last_message'")

@admin.register(HarvestJob)
class HarvestJobAdmin(admin.ModelAdmin):
    list_display = ("source","query","enabled","schedule","last_status","last_run","next_run")
    list_filter  = ("enabled","source__name","last_status")
    search_fields = ("query",)
    actions = [run_harvest_now]
    autocomplete_fields = ("source",)
    fieldsets = (
        (None, {"fields": ("source","query")}),
        ("Paramètres", {"fields": ("rows","max_pages","max_items","since","incremental")}),
        ("Planification", {"fields": ("enabled","schedule","next_run")}),
        ("Suivi", {"fields": ("last_status","last_run","last_message"), "classes": ("collapse",)}),
    )

