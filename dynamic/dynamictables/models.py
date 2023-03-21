from django.db import models

# Create your models here.

DT_STATE_NEW = "NEW"
DT_STATE_CREATED = "CRE"
DT_STATE_DELETED = "DEL"

class DynamicTableTable(models.Model):
    uuid = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    schema = models.JSONField()
    