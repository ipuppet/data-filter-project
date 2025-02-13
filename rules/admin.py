from django.contrib import admin
from django.utils.translation import gettext as _
import nested_admin

from .forms import ConditionGroupForm
from .models import Field, FieldMapper, Rule, ConditionGroup, Condition


class FieldMapperInline(admin.TabularInline):
    model = FieldMapper
    extra = 0
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

    @admin.display(description=_("Mapped values"))
    def get_mapped_values(self, obj):
        return ", ".join([m.value for m in obj.mapped_values.all()])


class ConditionInline(nested_admin.NestedStackedInline):
    model = Condition
    extra = 0
    fields = [
        "condition_type",
        "field",
        "operator",
        "value",
        ("temporal_unit", "temporal_window"),
        ("aggregation_type"),
        "custom_expression",
    ]
    classes = ["collapse"]


class ConditionGroupInline(nested_admin.NestedTabularInline):
    model = ConditionGroup
    extra = 0
    fields = ["rule", "logic_type", "parent_group", "order"]
    inlines = [ConditionInline]
    form = ConditionGroupForm


@admin.register(Rule)
class RuleAdmin(nested_admin.NestedModelAdmin):
    list_display = ("name", "id", "description", "created_at", "updated_at")
    inlines = [ConditionGroupInline]
    save_on_top = True
