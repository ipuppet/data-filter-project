from django.db import models, transaction
from django.utils.translation import gettext as _


class FieldManager(models.Manager):
    def create_with_mapped_values(self, name, description, data_type, mapped_values):
        with transaction.atomic():
            field = self.create(name=name, description=description, data_type=data_type)
            for mapper in mapped_values:
                FieldMapper.objects.create(field=field, **mapper)
            return field

    def update_with_mapped_values(
        self, field, name, description, data_type, mapped_values
    ):
        with transaction.atomic():
            field.name = name
            field.description = description
            field.data_type = data_type
            field.save()

            # 清除旧映射
            field.mapped_values.all().delete()
            for mapper in mapped_values:
                FieldMapper.objects.create(field=field, **mapper)
            return field


class Field(models.Model):
    DATA_TYPES = [
        ("NUMERIC", _("Numeric")),
        ("DATETIME", _("Datetime")),
        ("TEXT", _("Text")),
    ]
    objects = FieldManager()

    name = models.CharField(max_length=200, unique=True, verbose_name=_("Field name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    data_type = models.CharField(
        max_length=20, choices=DATA_TYPES, verbose_name=_("Data type")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Creation time")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Update time"))

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")

    def __str__(self):
        return self.name


class FieldMapper(models.Model):
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name="mapped_values",
        verbose_name=_("Field"),
    )
    value = models.CharField(
        max_length=200, verbose_name=_("Mapped value")
    )  # field name from the data source

    class Meta:
        verbose_name = _("Field mapper")
        verbose_name_plural = _("Field mappers")

    def __str__(self):
        return f"{self.field} -> {self.value}"


class RuleManager(models.Manager):
    def create_with_condition_groups(self, name, description, condition_groups):
        with transaction.atomic():
            rule = self.create(name=name, description=description)
            for idx, group in enumerate(condition_groups):
                self._build_condition_tree(rule, None, group, idx)
            return rule

    def update_with_condition_groups(self, rule, name, description, condition_groups):
        with transaction.atomic():
            rule.name = name
            rule.description = description
            rule.save()

            # 清除旧结构
            rule.condition_groups.all().delete()
            for idx, group in enumerate(condition_groups):
                self._build_condition_tree(rule, None, group, idx)
            return rule

    def _build_condition_tree(self, rule, parent_group, node, order=0):
        if "conditions" in node:
            group = ConditionGroup.objects.create(
                rule=rule,
                parent_group=parent_group,
                logic_type=node.get("logic_type", "AND"),
                order=order,
            )
            for idx, child in enumerate(node.get("conditions", [])):
                self._build_condition_tree(rule, group, child, idx)
        else:
            Condition.objects.create(
                group=parent_group, **{k: v for k, v in node.items() if k != "type"}
            )


class Rule(models.Model):
    objects = RuleManager()

    name = models.CharField(max_length=200, unique=True, verbose_name=_("Rule name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Creation time")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Update time"))

    class Meta:
        verbose_name = _("Rule")
        verbose_name_plural = _("Rules")

    def __str__(self):
        return self.name


class ConditionGroup(models.Model):
    LOGIC_TYPE_CHOICES = [
        ("AND", _("Match all conditions")),
        ("OR", _("Match at least one condition")),
        ("NOT", _("Exclude all matching conditions")),
    ]

    rule = models.ForeignKey(
        Rule,
        on_delete=models.CASCADE,
        related_name="condition_groups",
        verbose_name=_("Rule"),
    )
    parent_group = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Parent group"),
    )
    logic_type = models.CharField(
        max_length=10, choices=LOGIC_TYPE_CHOICES, verbose_name=_("Logic type")
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))

    class Meta:
        verbose_name = _("Rule group")
        verbose_name_plural = _("Rule groups")

    def __str__(self):
        return f"Group {self.id}"


class Condition(models.Model):
    CONDITION_TYPES = [
        ("BASIC", _("Field match")),
        ("TEMPORAL", _("Temporal match")),
        ("CUSTOM_SQL", _("Raw SQL expression")),
    ]
    TEMPORAL_UNITS = [
        ("day", _("Day")),
        ("month", _("Month")),
        ("year", _("Year")),
    ]
    AGGREGATION_TYPES = [
        ("COUNT", _("Count")),
        ("SUM", _("Sum")),
        ("AVG", _("Average")),
        ("MIN", _("Minimum value")),
        ("MAX", _("Maximum value")),
    ]
    OPERATORS = [
        ("==", "=="),
        (">", ">"),
        ("<", "<"),
        (">=", ">="),
        ("<=", "<="),
        ("!=", "!="),
        ("contains", _("Contains")),
        ("not_contains", _("Not contains")),
        ("regex", _("Regex match")),
    ]

    # 基础字段
    condition_type = models.CharField(
        max_length=20, choices=CONDITION_TYPES, verbose_name=_("Condition type")
    )
    group = models.ForeignKey(
        ConditionGroup,
        on_delete=models.CASCADE,
        related_name="conditions",
        verbose_name=_("Group"),
    )

    # 基本条件配置
    field = models.ForeignKey(
        Field, null=True, on_delete=models.SET_NULL, verbose_name=_("Field")
    )
    operator = models.CharField(
        max_length=20, choices=OPERATORS, verbose_name=_("Operator")
    )
    value = models.CharField(
        max_length=1000, blank=True, null=True, verbose_name=_("Value")
    )

    # 增强功能字段
    temporal_unit = models.CharField(
        max_length=10,
        choices=TEMPORAL_UNITS,
        blank=True,
        null=True,
        verbose_name=_("Temporal unit"),
    )
    temporal_window = models.IntegerField(
        blank=True, null=True, verbose_name=_("Temporal window")
    )  # 时间窗口数值
    aggregation_type = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=AGGREGATION_TYPES,
        verbose_name=_("Aggregation type"),
    )

    # 表达式配置
    custom_expression = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Custom expression"),
        help_text=_("Raw SQL expression"),
    )

    class Meta:
        verbose_name = _("Condition")
        verbose_name_plural = _("Conditions")

    def __str__(self):
        return f"{self.field} {self.operator} {self.value}"
