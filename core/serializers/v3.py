from django.db.models import Q
from rest_framework import fields, serializers

from .. import models
from .fields import InvisibleCharField
from .dict_serializer import DictSerializer


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.V3Resource
        list_serializer_class = DictSerializer
        many_key_field = 'key'
        fields = [
            'key',
            'depends_on',
            'primary',
            'provider',
            'type',
        ]

    key = InvisibleCharField()
    depends_on = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=True)
    primary = serializers.DictField(allow_empty=True, required=True)
    provider = serializers.CharField(required=True)
    type = serializers.CharField(required=True)


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Module
        fields = [
            'depends_on',
            'outputs',
            'path',
            'resources',
        ]

    depends_on = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)
    outputs = serializers.DictField(allow_empty=True, required=True)
    path = serializers.ListField(child=serializers.CharField(), required=True)
    resources = ResourceSerializer(many=True, required=True)

    def create(self, validated_data):
        resources_data = validated_data.pop('resources')
        module = models.Module.objects.create(**validated_data)

        for key, resource_data in resources_data.items():
            resource_data['key'] = key
            self.serialize_resource(module, resource_data).save(module=module)

        self.remove_destoryed_resources(module, resources_data)
        return module

    def update(self, module, validated_data):
        resources_data = validated_data.pop('resources')
        module.depends_on = validated_data.get('depends_on', module.depends_on)
        module.outputs = validated_data.get('outputs', module.outputs)
        module.path = validated_data.get('path', module.path)
        module.save()

        for key, resource_data in resources_data.items():
            resource_data['key'] = key
            self.serialize_resource(module, resource_data).save(module=module)

        self.remove_destroyed_resources(module, resources_data)
        return module

    def serialize_resource(self, module, resource_data):
        key = resource_data['key']
        resource, _ = module.resources.get_or_create(
            module=module, key=key,
            defaults=resource_data
        )
        resource_serializer = ResourceSerializer(resource, data=resource_data)

        resource_serializer.is_valid()
        return resource_serializer

    def remove_destroyed_resources(self, module, resources_data):
        resource_type_module_keys = [(r['type'], r['key']) for r in resources_data.values()]
        resources_to_delete = module.resources
        for type, key in resource_type_module_keys:
            q_exclude = Q(type=type) & Q(module=module) & Q(key=key)
            resources_to_delete = resources_to_delete.exclude(q_exclude)
        resources_to_delete.all().delete()


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.State
        fields = [
            'lineage',
            'terraform_version',
            'version',
            'serial',
            'modules',
        ]

    lineage = serializers.UUIDField(required=True)
    terraform_version = serializers.CharField(max_length=256)
    version = serializers.IntegerField(required=True)
    serial = serializers.IntegerField(required=True)
    modules = ModuleSerializer(many=True)

    def create(self, validated_data):
        modules_data = validated_data.pop('modules')
        state = models.State.objects.create(**validated_data)

        for module_data in modules_data:
            self.serialize_module(state, module_data).save(state=state)

        self.remove_destroyed_modules(state, modules_data)
        return state

    def update(self, state, validated_data):
        modules_data = validated_data.pop('modules')

        state.lineage = validated_data.get('lineage', state.lineage)
        state.serial = validated_data.get('serial', state.serial)
        state.version = validated_data.get('version', state.version)
        state.terraform_version = validated_data.get('terraform_version', state.terraform_version)
        state.raw = validated_data.get('raw', state.raw)
        state.save()

        for module_data in modules_data:
            self.serialize_module(state, module_data).save(state=state)

        self.remove_destroyed_modules(state, modules_data)
        return state

    def serialize_module(self, state, module_data):
        module, _ = state.modules.get_or_create(path=module_data['path'])
        module_serializer = ModuleSerializer(module, data=module_data)

        module_serializer.is_valid(raise_exception=True)
        return module_serializer

    def remove_destroyed_modules(self, state, modules_data):
        module_paths = [m['path'] for m in modules_data]
        state.modules.exclude(path__in=module_paths).delete()
