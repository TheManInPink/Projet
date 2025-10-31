from django.db import models
from django.utils import timezone


class DataSource(models.Model):
    CKAN = 'CKAN'
    DATAVERSE = 'DATAVERSE'
    KIND_CHOICES = [(CKAN, 'CKAN'), (DATAVERSE, 'Dataverse')]

    name = models.CharField(max_length=100, unique=True)
    base_url = models.URLField()
    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    notes = models.TextField(blank=True)

    last_success_at = models.DateTimeField(null=True, blank=True)
    last_modified_cursor = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.name} ({self.kind})"


class Dataset(models.Model):
    source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    # external_id = models.CharField(max_length=255, db_index=True)
    external_id = models.CharField(max_length=191, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    keywords = models.JSONField(default=list) # nécessite MySQL 8.0+ pour JSON natif
    organization = models.CharField(max_length=191, blank=True)
    license = models.CharField(max_length=255, blank=True)
    # url = models.URLField(blank=True)
    url = models.URLField(blank=True, max_length=2048)
    extras = models.JSONField(default=dict)
    created_at_src = models.DateTimeField(null=True, blank=True)
    modified_at_src = models.DateTimeField(null=True, blank=True)
    harvested_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('source', 'external_id')]
        ordering = ['-harvested_at']

        indexes = [
            models.Index(fields=['source', 'harvested_at']),
            models.Index(fields=['organization']),
        ]


    def __str__(self):
        return self.title


class HarvestingLog(models.Model):
    PENDING='PENDING'; OK='OK'; ERROR='ERROR'
    STATUS_CHOICES=[(PENDING,'PENDING'),(OK,'OK'),(ERROR,'ERROR')]


    created_at = models.DateTimeField(auto_now_add=True)
    source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True)
    query = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    items_found = models.PositiveIntegerField(default=0)
    message = models.TextField(blank=True)
    payload = models.JSONField(default=dict)


    class Meta:
        ordering = ['-created_at']


class HarvestJob(models.Model):
    source = models.ForeignKey('DataSource', on_delete=models.CASCADE)
    query = models.CharField(max_length=300, blank=True, help_text="q CKAN/Dataverse")
    rows = models.PositiveIntegerField(default=100)
    max_pages = models.PositiveIntegerField(default=5)
    max_items = models.PositiveIntegerField(default=500)
    since = models.DateTimeField(null=True, blank=True, help_text="Ignorer plus ancien")
    incremental = models.BooleanField(default=True, help_text="Utilise last_modified_cursor si dispo")

    enabled = models.BooleanField(default=True)
    schedule = models.CharField(max_length=64, blank=True, help_text="Note libre (ex: 0 2 * * *)")

    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(
        max_length=10,
        choices=[('PENDING','PENDING'),('OK','OK'),('ERROR','ERROR')],
        default='PENDING'
    )
    last_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.source.name} / {self.query or '*'}"