from django.db.models import Q
from rest_framework import fields, serializers

from .. import models
from .fields import OptionalCharField, OptionalIntegerField

class InstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instance
        fields = [
            'schema_version',
            'attributes',
            'index_key',
            'private',
            'depends_on',
        ]

    schema_version = serializers.IntegerField(required=True)
    attributes = serializers.DictField(allow_empty=True, required=True)
    index_key = OptionalIntegerField(required=False)
    private = serializers.CharField(required=True)
    depends_on = serializers.ListField(child=serializers.CharField(), required=False)


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Resource
        fields = [
            'each',
            'mode',
            'type',
            'module',
            'name',
            'provider',
            'instances',
        ]

    each = OptionalCharField(required=False)
    mode = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    module = OptionalCharField(required=False)
    name = serializers.CharField(required=True)
    provider = serializers.CharField(required=True)
    instances = InstanceSerializer(many=True)

    def create(self, validated_data):
        instances_data = validated_data.pop('instances')
        resource = models.Resource.objects.create(**validated_data)

        for instance_data in instances_data:
            self.serialize_instance(resource, instance_data).save(resource=resource)

        self.remove_destroyed_instances(resource, instances_data)
        return resource

    def update(self, resource, validated_data):
        instances_data = validated_data.pop('instances')

        resource.each = validated_data.get('each', resource.each)
        resource.mode = validated_data.get('mode', resource.mode)
        resource.type = validated_data.get('type', resource.type)
        resource.module = validated_data.get('module', resource.module)
        resource.name = validated_data.get('name', resource.name)
        resource.provider = validated_data.get('provider', resource.provider)
        resource.save()

        for instance_data in instances_data:
            self.serialize_instance(resource, instance_data).save(resource=resource)

        self.remove_destroyed_instances(resource, instances_data)
        return resource

    def serialize_instance(self, resource, instance_data):
        index_key = instance_data.get('index_key')
        instance_data['attribute_id'] = instance_data['attributes']['id']
        instance, _ = resource.instances.get_or_create(
            resource=resource, index_key=index_key, defaults=instance_data)
        instance_serializer = InstanceSerializer(instance, data=instance_data)

        instance_serializer.is_valid()
        return instance_serializer

    def remove_destroyed_instances(self, resource, instances_data):
        attribute_ids = {i['attributes']['id'] for i in instances_data}
        resource.instances.exclude(attribute_id__in=attribute_ids).delete()


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.State
        fields = [
            'lineage',
            'terraform_version',
            'version',
            'serial',
            'outputs',
            'resources',
        ]

    lineage = serializers.UUIDField(required=True)
    terraform_version = serializers.CharField(max_length=256)
    version = serializers.IntegerField(required=True)
    serial = serializers.IntegerField(required=True)
    outputs = serializers.DictField(required=True)
    resources = ResourceSerializer(many=True)

    def create(self, validated_data):
        resources_data = validated_data.pop('resources')
        state = models.State.objects.create(**validated_data)

        for resource_data in resources_data:
            self.serialize_resource(state, resource_data).save(state=state)

        self.remove_destroyed_resources(state, resources_data)
        return state

    def update(self, state, validated_data):
        resources_data = validated_data.pop('resources')

        state.lineage = validated_data.get('lineage', state.lineage)
        state.serial = validated_data.get('serial', state.serial)
        state.version = validated_data.get('version', state.version)
        state.terraform_version = validated_data.get('terraform_version', state.terraform_version)
        state.outputs = validated_data.get('outputs', state.outputs)
        state.raw = validated_data.get('raw', state.raw)
        state.save()

        for resource_data in resources_data:
            self.serialize_resource(state, resource_data).save(state=state)

        self.remove_destroyed_resources(state, resources_data)
        return state

    def serialize_resource(self, state, resource_data):
        type = resource_data['type']
        module = resource_data['module']
        name = resource_data['name']
        resource, _ = state.resources.get_or_create(
            type=type, module=module, name=name,
            defaults={
                'mode': resource_data['mode'],
                'provider': resource_data['provider']
            },
        )
        resource_serializer = ResourceSerializer(resource, data=resource_data)

        resource_serializer.is_valid()
        return resource_serializer

    def remove_destroyed_resources(self, state, resources_data):
        resource_type_module_names = [(r['type'], r['module'], r['name']) for r in resources_data]
        resources_to_delete = state.resources
        for type, module, name in resource_type_module_names:
            q_exclude = Q(type=type) & Q(module=module) & Q(name=name)
            resources_to_delete = resources_to_delete.exclude(q_exclude)
        resources_to_delete.delete()
