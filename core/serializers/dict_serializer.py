from rest_framework import serializers


class DictSerializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_error_messages['not_a_dict'] = 'Expected a dict of items but got type "{input_type}".'

    def get_initial(self):
        if hasattr(self, 'initial_data'):
            return self.to_representation(self.initial_data)
        return {}

    def to_representation(self, data):
        many_key_field = self.child.Meta.many_key_field

        return {
            getattr(item, many_key_field): self.child.to_representation(item)
            for item in data.all()
        }

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            message = self.error_messages['not_a_dict'].format(
                input_type=type(data).__name__
            )
            raise serializers.ValidationError({
                serializers.api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='not_a_dict')

        ret = {}
        errors = []
        many_key_field = self.child.Meta.many_key_field
        for key, item in data.items():
            try:
                item[many_key_field] = key
                validated = self.child.run_validation(item)
            except serializers.ValidationError as exc:
                errors.append(exc.detail)
            else:
                ret[key] = validated
                errors.append({})

        if any(errors):
            raise serializers.ValidationError(errors)

        return ret

    def create(self, validated_data):
        many_key_field = self.child.Meta.many_key_field
        return {
            getattr(item, many_key_field): self.child.create(attrs)
            for attrs in validated_data
        }



