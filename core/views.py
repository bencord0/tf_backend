import json

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import views, viewsets
from rest_framework.response import Response

from . import models, serializers


class StateViewSet(viewsets.ModelViewSet):
    queryset = models.State.objects.all()

    def get_serializer_class(self):
        # Use a smaller serializer to determine which serializer to use
        # If both are needed, only render the common/required fields
        if len(self.queryset.values_list('version').distinct()) > 1:
            return serializers.VersionSerializer

        version, = self.queryset.values_list('version').distinct().get()
        return serializers.get_serializers(version)


class Index(views.APIView):
    def get(self, request, scope):
        state = get_object_or_404(models.State, pk=scope)
        request_serializers = serializers.get_serializers(state.version)
        state_serializer = request_serializers.StateSerializer(state)
        return Response(state_serializer.data)

    @transaction.atomic
    def post(self, request, scope):
        # A small serializer to determine which serializer to use
        version_serializer = serializers.VersionSerializer(data=request.data)
        version_serializer.is_valid(raise_exception=True)

        state, _ = models.State.objects.get_or_create(
            scope=scope, defaults=version_serializer.validated_data,
        )

        request_serializers = serializers.get_serializers(
            version_serializer.validated_data['version']
        )

        serializer = request_serializers.StateSerializer(state, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(scope=scope, raw=request.data)
        return HttpResponse("");

    @transaction.atomic
    def delete(self, request, scope):
        get_object_or_404(models.State, pk=scope).delete()
        return HttpResponse("")
