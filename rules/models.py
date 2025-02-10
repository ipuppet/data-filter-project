from django.db import models, transaction


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
        ("NUMERIC", "Numeric value"),
        ("TEMPORAL", "Date/time"),
        ("CATEGORICAL", "Discrete values"),
        ("TEXT", "Free text"),
    ]
    objects = FieldManager()

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    data_type = models.CharField(max_length=20, choices=DATA_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FieldMapper(models.Model):
    field = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name="mapped_values"
    )
    value = models.CharField(max_length=200)  # field name from the data source

    def __str__(self):
        return f"{self.field} - {self.value}"


class RuleManager(models.Manager):
    def create_with_condition_groups(self, name, description, condition_groups):
        """
        参数示例：
        condition_groups = {
            "type": "GROUP",
            "logic_type": "AND",
            "conditions": [
                {
                    "type": "GROUP",
                    "logic_type": "OR",
                    "conditions": [
                        {
                            "type": "CONDITION",
                            "field_id": 1,
                            "operator": ">",
                            "value": 100,
                            "condition_type": "BASIC"
                        }
                    ]
                },
                {
                    "type": "CONDITION",
                    "field_id": 2,
                    "operator": "==",
                    "value": "unpaid",
                    "condition_type": "BASIC"
                }
            ]
        }
        """
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

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ConditionGroup(models.Model):
    LOGIC_TYPE_CHOICES = [
        ("AND", "All conditions must be true"),
        ("OR", "Any condition can be true"),
        ("NOT", "Negate the result"),
    ]

    rule = models.ForeignKey(
        Rule, on_delete=models.CASCADE, related_name="condition_groups"
    )
    parent_group = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    logic_type = models.CharField(max_length=10, choices=LOGIC_TYPE_CHOICES)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Group {self.id}"


class Condition(models.Model):
    CONDITION_TYPES = [
        ("BASIC", "Field comparison"),
        ("AGGREGATE", "Aggregate function"),
        ("TEMPORAL", "Time-based rule"),
        ("RELATIONAL", "Cross-record check"),
        ("EXISTS", "Existence check"),
        ("CUSTOM_SQL", "Raw SQL expression"),
        ("COMPOSITE", "Nested logic group"),
    ]
    TEMPORAL_UNITS = [
        ("day", "Day"),
        ("month", "Month"),
        ("year", "Year"),
    ]
    AGGREGATION_TYPES = [
        ("COUNT", "Count"),
        ("SUM", "Sum"),
        ("AVG", "Average"),
        ("MIN", "Minimum"),
        ("MAX", "Maximum"),
    ]

    # 基础字段
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES)
    group = models.ForeignKey(
        ConditionGroup, on_delete=models.CASCADE, related_name="conditions"
    )

    # 基本条件配置
    field = models.ForeignKey(Field, null=True, on_delete=models.SET_NULL)
    operator = models.CharField(max_length=20)  # 支持扩展如：contains, regex, in
    value = models.JSONField(blank=True, null=True)  # 支持多值比较

    # 增强功能字段
    temporal_unit = models.CharField(
        max_length=10, choices=TEMPORAL_UNITS, blank=True, null=True
    )
    temporal_window = models.IntegerField(blank=True, null=True)  # 时间窗口数值
    aggregation_type = models.CharField(
        max_length=20, blank=True, null=True, choices=AGGREGATION_TYPES
    )

    # 表达式配置
    custom_expression = models.TextField(blank=True, null=True)  # 自定义SQL片段

    def __str__(self):
        return f"{self.field} {self.operator} {self.value}"
