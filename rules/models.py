from django.db import models, transaction


class Field(models.Model):
    DATA_TYPES = [
        ("NUMERIC", "Numeric value"),
        ("TEMPORAL", "Date/time"),
        ("CATEGORICAL", "Discrete values"),
        ("TEXT", "Free text"),
    ]

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    data_type = models.CharField(max_length=20, choices=DATA_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FieldMapper(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)  # field name from the data source

    def __str__(self):
        return f"{self.field} - {self.value}"


class RuleManager(models.Manager):
    def create_with_conditions(self, name, description, condition_tree):
        """
        参数示例：
        condition_tree = {
            "logic_type": "AND",
            "children": [
                {
                    "type": "GROUP",
                    "logic_type": "OR",
                    "conditions": [
                        {
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
            self._build_condition_tree(rule, None, condition_tree)
            return rule

    def update_with_conditions(self, rule, name, description, condition_tree):
        with transaction.atomic():
            rule.name = name
            rule.description = description
            rule.save()

            # 清除旧结构
            rule.condition_groups.all().delete()
            self._build_condition_tree(rule, None, condition_tree)
            return rule

    def _build_condition_tree(self, rule, parent_group, node, order=0):
        if node.get("type") == "GROUP" or "children" in node:
            group = ConditionGroup.objects.create(
                rule=rule,
                parent_group=parent_group,
                logic_type=node.get("logic_type", "AND"),
                order=order,
            )

            for idx, child in enumerate(node.get("children", [])):
                self._build_condition_tree(rule, group, child, idx)

        else:
            Condition.objects.create(
                group=parent_group, **{k: v for k, v in node.items() if k != "type"}
            )


class Rule(models.Model):
    objects = RuleManager()

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    base_table = models.CharField(max_length=200)
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

    parent_group = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="child_groups",
    )
    logic_type = models.CharField(max_length=10, choices=LOGIC_TYPE_CHOICES)
    rule = models.ForeignKey(
        Rule, on_delete=models.CASCADE, related_name="condition_groups"
    )
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
    aggregation_type = models.CharField(max_length=20, blank=True, null=True)
    related_field = models.CharField(
        max_length=200, blank=True, null=True
    )  # 关联字段路径

    # 表达式配置
    custom_expression = models.TextField(blank=True, null=True)  # 自定义SQL片段

    def __str__(self):
        return f"{self.field} {self.operator} {self.value}"
