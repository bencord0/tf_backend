from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField


class State(models.Model):
    class Meta:
        unique_together = [
            ['scope', 'lineage', 'serial'],
        ]

    scope = models.TextField(primary_key=True)
    lineage = models.UUIDField(editable=False)
    serial = models.IntegerField(editable=False)
    version = models.IntegerField(editable=False)
    terraform_version = models.TextField(editable=False)
    outputs = JSONField(default=dict)
    raw = JSONField(null=True, blank=True)


class Resource(models.Model):
    class Meta:
        unique_together = [
            ['state', 'type', 'module', 'name'],
        ]

    state = models.ForeignKey(State, related_name='resources', on_delete=models.CASCADE)
    mode = models.TextField(editable=False)
    type = models.TextField(editable=False)
    module = models.TextField(editable=False, null=True)
    name = models.TextField(editable=False)
    provider = models.TextField(editable=False)
    each = models.TextField(editable=False, null=True)


class Instance(models.Model):
    class Meta:
        unique_together = [
            ['resource', 'index_key'],
            ['resource', 'index_key', 'attribute_id'],
        ]
    resource = models.ForeignKey(Resource, related_name='instances', on_delete=models.CASCADE)
    schema_version = models.IntegerField(editable=False)
    index_key = models.IntegerField(null=True, editable=False)
    attribute_id = models.TextField(editable=False)
    private = models.TextField(editable=False)
    attributes = JSONField()
    depends_on = ArrayField(models.TextField(), default=list)


class Module(models.Model):
    class Meta:
        unique_together = [
            ['state', 'path'],
        ]
    state = models.ForeignKey(State, related_name='modules', on_delete=models.CASCADE)
    depends_on = ArrayField(models.TextField(), default=list)
    outputs = JSONField(default=dict)
    path = ArrayField(models.TextField(), default=list)


class V3Resource(models.Model):
    class Meta:
        unique_together = [
            ['module', 'key'],
            ['module', 'type', 'key'],
        ]
    module = models.ForeignKey(Module, related_name='resources', on_delete=models.CASCADE)
    key = models.TextField(editable=False)
    depends_on = ArrayField(models.TextField(), default=list)
    # deposed = Arrayfield(???)
    primary = JSONField()
    provider = models.TextField(editable=False)
    type = models.TextField(editable=False)
