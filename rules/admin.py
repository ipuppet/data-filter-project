from django.contrib import admin
import nested_admin
from .models import Field, FieldMapper, Rule, ConditionGroup, Condition


class FieldMapperInline(admin.TabularInline):
    model = FieldMapper
    extra = 1
    fields = ("field", "value")


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "data_type",
        "get_mapped_values",
        "created_at",
        "updated_at",
    )
    inlines = [FieldMapperInline]

    @admin.display(description="Mapped Values")
    def get_mapped_values(self, obj):
        return ", ".join([m.value for m in obj.fieldmapper_set.all()])


class ConditionInline(nested_admin.NestedStackedInline):
    model = Condition
    extra = 0
    fields = [
        "condition_type",
        "field",
        "operator",
        "value",
        ("temporal_unit", "temporal_window"),
        ("aggregation_type", "related_field"),
        "custom_expression",
    ]


class ConditionGroupInline(nested_admin.NestedTabularInline):
    model = ConditionGroup
    extra = 0
    fields = ["logic_type", "parent_group", "order"]
    inlines = [ConditionInline]


@admin.register(Rule)
class RuleAdmin(nested_admin.NestedModelAdmin):
    list_display = ("name", "description", "created_at", "updated_at")
    inlines = [ConditionGroupInline]
    save_on_top = True
