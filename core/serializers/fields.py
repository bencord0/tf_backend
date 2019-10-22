from rest_framework import fields, serializers


class InvisibleCharField(serializers.CharField):
    def get_attribute(self, instance):
        raise fields.SkipField()


class OptionalGetAttribute:
    def get_attribute(self, instance):
        attr = super().get_attribute(instance)
        if attr is None:
            raise fields.SkipField()
        return attr


class OptionalIntegerField(OptionalGetAttribute, serializers.IntegerField):
    pass


class OptionalCharField(OptionalGetAttribute, serializers.CharField):
    pass
