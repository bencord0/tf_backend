from rest_framework import serializers
from . import v3, v4

SERIALIZERS_VERSIONS = {
    3: v3,
    4: v4,
}


def get_serializers(version):
    return SERIALIZERS_VERSIONS[version]
    serializer = VersionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    version = serializer.validated_data['version']


class VersionSerializer(serializers.Serializer):
    lineage = serializers.UUIDField(required=True)
    terraform_version = serializers.CharField(max_length=256)
    serial = serializers.IntegerField(required=True)
    version = serializers.IntegerField(required=True)
