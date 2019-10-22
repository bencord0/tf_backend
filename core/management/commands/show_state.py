from django.core.management.base import BaseCommand
from rest_framework.renderers import JSONRenderer

from core.models import State
from core.serializers import get_serializers

renderer = JSONRenderer()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('scope', type=str)

    def handle(self, *args, **options):
        state = State.objects.get(pk=options['scope'])
        serializers = get_serializers(state.version)
        serializer = serializers.StateSerializer(state)

        self.stdout.write(
            renderer.render(
                serializer.data, renderer_context={'indent': 4}
            ).decode()
        )
