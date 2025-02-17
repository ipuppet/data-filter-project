from rest_framework import serializers

from .models import ConditionGroup, Rule, Field, FieldMapper, Condition


class FieldMapperSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldMapper
        fields = ["value"]


class FieldSerializer(serializers.ModelSerializer):
    mapped_values = FieldMapperSerializer(many=True)

    class Meta:
        model = Field
        fields = [
            "id",
            "name",
            "description",
            "data_type",
            "mapped_values",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        mapped_values = validated_data.pop("mapped_values", [])
        return Field.objects.create_with_mapped_values(
            name=validated_data["name"],
            description=validated_data.get("description", ""),
            data_type=validated_data["data_type"],
            mapped_values=mapped_values,
        )

    def update(self, instance, validated_data):
        mapped_values = validated_data.pop("mapped_values", [])
        return Field.objects.update_with_mapped_values(
            field=instance,
            name=validated_data.get("name", instance.name),
            description=validated_data.get("description", instance.description),
            data_type=validated_data.get("data_type", instance.data_type),
            mapped_values=mapped_values,
        )


class ConditionSerializer(serializers.ModelSerializer):
    field = serializers.PrimaryKeyRelatedField(queryset=Field.objects.all())

    class Meta:
        model = Condition
        fields = [
            "condition_type",
            "field",
            "operator",
            "value",
            "temporal_unit",
            "temporal_window",
            "aggregation_type",
            "custom_expression",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["field"] = FieldSerializer(instance.field).data
        return representation


class ConditionGroupSerializer(serializers.ModelSerializer):
    conditions = ConditionSerializer(many=True)

    class Meta:
        model = ConditionGroup
        fields = ["id", "parent_group", "logic_type", "order", "conditions"]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["conditions"] = ConditionSerializer(
            instance.conditions.all(), many=True
        ).data
        return representation


class RuleSerializer(serializers.ModelSerializer):
    condition_groups = ConditionGroupSerializer(many=True)

    class Meta:
        model = Rule
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "condition_groups",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        condition_groups = validated_data.pop("condition_groups", [])
        rule = Rule.objects.create_with_condition_groups(
            name=validated_data["name"],
            description=validated_data["description"],
            condition_groups=condition_groups,
        )
        return rule

    def update(self, instance, validated_data):
        condition_groups = validated_data.pop("condition_groups", [])
        rule = Rule.objects.update_with_condition_groups(
            rule=instance,
            name=validated_data.get("name", instance.name),
            description=validated_data.get("description", instance.description),
            condition_groups=condition_groups,
        )
        return rule
