from django.contrib import admin
from .models import Field, FieldMapper, Rule, Condition


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(FieldMapper)
class FieldMapperAdmin(admin.ModelAdmin):
    list_display = ("field", "value")


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ("rule", "field", "value", "operator", "required")
