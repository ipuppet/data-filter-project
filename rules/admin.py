from django.contrib import admin
from .models import Field, FieldMapper, Rule, Condition


class FieldMapperAdmin(admin.ModelAdmin):
    list_display = ("field", "value")


class RuleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


class ConditionAdmin(admin.ModelAdmin):
    list_display = ("rule", "field", "value", "operator", "required")


admin.site.register(Field)
admin.site.register(FieldMapper, FieldMapperAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(Condition, ConditionAdmin)
