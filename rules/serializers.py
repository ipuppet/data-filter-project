from rest_framework import serializers
from .models import Rule, Field, FieldMapper, Condition


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ["id", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class FieldMapperSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldMapper
        fields = ["field", "value"]


class ConditionSerializer(serializers.ModelSerializer):
    field = serializers.PrimaryKeyRelatedField(queryset=Field.objects.all())

    class Meta:
        model = Condition
        fields = ["field", "value", "operator", "required"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["field"] = FieldSerializer(instance.field).data
        return representation


class RuleSerializer(serializers.ModelSerializer):
    conditions = ConditionSerializer(many=True)

    class Meta:
        model = Rule
        fields = ["id", "name", "description", "created_at", "updated_at", "conditions"]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        conditions_data = validated_data.pop("conditions", [])
        rule = Rule.objects.create_with_conditions(
            name=validated_data["name"],
            description=validated_data["description"],
            conditions_data=conditions_data,
        )
        return rule

    def update(self, instance, validated_data):
        conditions_data = validated_data.pop("conditions", [])
        rule = Rule.objects.update_with_conditions(
            rule=instance,
            name=validated_data.get("name", instance.name),
            description=validated_data.get("description", instance.description),
            conditions_data=conditions_data,
        )
        return rule
