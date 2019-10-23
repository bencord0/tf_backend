from django.core.management.base import BaseCommand
from guardian.shortcuts import assign_perm
from pprint import pformat

from core.models import State
from core.serializers import get_serializers


class Command(BaseCommand):
    def handle(self, *args, **options):
        for state in State.objects.all():
            serializers = get_serializers(state.version)
            serializer = serializers.StateSerializer(state, state.raw)
            serializer.is_valid(raise_exception=True)

            if state.owner:
                assign_perm('add_state', state.owner, state)
                assign_perm('change_state', state.owner, state)
                assign_perm('delete_state', state.owner, state)
                assign_perm('view_state', state.owner, state)

            serializer.save()
