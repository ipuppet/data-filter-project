from django.contrib import admin
from .models import Field, FieldMapper, Rule, Condition


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(FieldMapper)
class FieldMapperAdmin(admin.ModelAdmin):
    list_display = ("field", "value")


class ConditionInline(admin.TabularInline):
    model = Condition
    extra = 1


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at", "updated_at")
    inlines = [ConditionInline]
