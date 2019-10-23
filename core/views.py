import json

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from guardian.shortcuts import get_objects_for_user

from . import models, serializers


class Index(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return get_objects_for_user(
            self.request.user,
            ['view_state', 'add_state', 'change_state', 'delete_state'],
            klass=models.State)

    def get_serializer_class(self):
        # Use a smaller serializer to determine which serializer to use
        # If both are needed, only render the common/required fields
        queryset = self.filter_queryset(self.get_queryset())
        if len(queryset.values_list('version').distinct()) > 1:
            return serializers.VersionSerializer

        obj = get_object_or_404(queryset)
        return serializers.get_serializers(obj.version).StateSerializer

    @transaction.atomic
    def post(self, request, pk):
        # A small serializer to determine which serializer to use
        version_serializer = serializers.VersionSerializer(data=request.data)
        version_serializer.is_valid(raise_exception=True)

        state, _ = models.State.objects.get_or_create(
            pk=pk, defaults=version_serializer.validated_data,
        )
        self.check_object_permissions(self.request, state)

        request_serializers = serializers.get_serializers(
            version_serializer.validated_data['version']
        )

        serializer = request_serializers.StateSerializer(state, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(pk=pk, raw=request.data)
        return Response(None, status=status.HTTP_204_NO_CONTENT)
