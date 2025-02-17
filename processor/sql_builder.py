import re
from datetime import datetime
from typing import Dict, Tuple, List
from django.db.models import QuerySet
from sqlalchemy import Table

from rules.models import ConditionGroup, Condition, Field


class InvalidValueError(Exception):
    pass


class SecurityError(Exception):
    pass


class SQLBuilder:
    def __init__(self, rule, target_table):
        self.rule = rule
        self.param_counter = 0
        self.target_table: Table = target_table

    def build(self) -> Tuple[str, Dict]:
        """查询生成"""
        root_groups = self.rule.condition_groups.filter(parent_group=None)
        where_clause, params = self.process_groups(root_groups)
        sql = f"SELECT * FROM `{self.target_table.name}` WHERE {where_clause}"
        return sql, params

    def process_groups(
        self, groups: QuerySet, parent_group: ConditionGroup = None
    ) -> Tuple[str, Dict]:
        """递归处理条件组"""
        conditions = []
        params = {}

        for group in groups.order_by("order"):
            group_clause, group_params = self._process_single_group(group)
            conditions.append(group_clause)
            params.update(group_params)

        if not conditions:
            return "", {}

        logic = parent_group.logic_type if parent_group else "AND"
        combined = self._combine_conditions(conditions, logic)

        return combined, params

    def _process_single_group(self, group: ConditionGroup) -> Tuple[str, Dict]:
        """处理单个条件组"""
        # 处理子组
        child_clause, child_params = self.process_groups(
            group.conditiongroup_set.all(), group
        )

        # 处理直接条件
        direct_clauses = []
        direct_params = {}
        for condition in group.conditions.all():
            clause, param = self._process_condition(condition)
            direct_clauses.append(clause)
            direct_params.update(param)

        return self._combine_group_conditions(
            group, child_clause, child_params, direct_clauses, direct_params
        )

    def _process_condition(self, condition: Condition) -> Tuple[str, Dict]:
        """条件分发处理器"""
        handlers = {
            "BASIC": self._handle_basic_condition,
            "TEMPORAL": self._handle_temporal_condition,
            "CUSTOM_SQL": self._handle_custom_sql,
        }
        return handlers[condition.condition_type](condition)

    def _handle_basic_condition(self, condition: Condition) -> Tuple[str, Dict]:
        """基础条件处理"""
        # 字段安全校验
        if not condition.field.mapped_values.exists():
            raise ValueError(f"Field {condition.field.name} has no mapped columns")

        # 处理聚合逻辑
        if condition.aggregation_type:
            return self._build_aggregation_condition(condition)

        return self._build_standard_condition(condition)

    def _build_aggregation_condition(self, condition: Condition) -> Tuple[str, Dict]:
        """构建聚合条件表达式"""
        column = self._get_mapped_column(condition.field)
        operator = condition.operator
        value = self._format_condition_value(condition)

        param_name = self._generate_param_name()

        agg_function = condition.aggregation_type.upper()
        return (
            f"{agg_function}({column}) {operator} :{param_name}",
            {param_name: value},
        )

    def _build_standard_condition(self, condition: Condition) -> Tuple[str, Dict]:
        """构建标准条件表达式"""
        column = self._get_mapped_column(condition.field)
        operator = condition.operator
        value = self._format_condition_value(condition)

        param_name = self._generate_param_name()
        return f"{column} {operator} :{param_name}", {param_name: value}

    def _handle_temporal_condition(self, condition: Condition) -> Tuple[str, Dict]:
        """时间条件"""
        column = self._get_mapped_column(condition.field)
        window = condition.temporal_window
        unit = condition.temporal_unit
        custom_datetime = datetime.strptime(
            self._format_condition_value(condition), "%Y-%m-%d %H:%M:%S"
        )
        formatted_date = custom_datetime.strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"{column} BETWEEN datetime('{formatted_date}', '-{window} {unit}') "
            f"AND datetime('{formatted_date}')"
        ), {}

    def _handle_custom_sql(self, condition: Condition) -> Tuple[str, Dict]:
        """自定义SQL处理"""
        # 允许常用运算符
        sanitized = re.sub(
            r"[^a-zA-Z0-9_(),.+*/%-=<> ]", "", condition.custom_expression
        )

        # 扩展禁止的关键字
        forbidden = {"DELETE", "UPDATE", "INSERT", "DROP", "ALTER", "GRANT"}
        for token in sanitized.upper().split():
            if token in forbidden:
                raise SecurityError(f"Forbidden SQL keyword: {token}")

        return f"({sanitized})", {}

    def _generate_param_name(self) -> str:
        """确保线程安全的参数名生成"""
        self.param_counter += 1
        return f"param_{self.param_counter}_{id(self)}"  # 增加实例ID防止冲突

    def _get_mapped_column(self, field: Field) -> str:
        """获取字段映射的首个可用列名"""
        for mapper in field.mapped_values.all():
            columns = self.target_table.columns.keys()
            if mapper.value in columns:
                return self._quote_column(mapper.value)
        raise ValueError(f"Field {field.name} has no mapped columns")

    def _format_condition_value(self, condition) -> any:
        """类型敏感的值格式化"""
        if condition.field.data_type == "NUMERIC":
            try:
                return float(condition.value)
            except ValueError:
                raise InvalidValueError(f"Invalid numeric value: {condition.value}")

        if condition.field.data_type == "DATETIME":
            if not re.match(r"\d{4}-\d{2}-\d{2}", condition.value):
                raise InvalidValueError(f"Invalid datetime format: {condition.value}")
            return condition.value

        return condition.value

    def _combine_conditions(self, conditions: List[str], logic: str) -> str:
        valid_conditions = [c for c in conditions if c]
        if not valid_conditions:
            return ""
        return (
            f"({f' {logic} '.join(valid_conditions)})"
            if len(valid_conditions) > 1
            else valid_conditions[0]
        )

    def _combine_group_conditions(
        self, group, child_clause, child_params, direct_clauses, direct_params
    ):
        """组合子条件和直接条件"""
        parts = []
        params = {}

        if child_clause:
            parts.append(child_clause)
            params.update(child_params)

        if direct_clauses:
            logic = f" {group.logic_type} "
            combined_direct = f"({logic.join(direct_clauses)})"
            parts.append(combined_direct)
            params.update(direct_params)

        if not parts:
            return "", {}

        group_logic = " AND " if group.logic_type == "AND" else " OR "
        final_clause = f"({group_logic.join(parts)})"

        return final_clause, params

    def _quote_column(self, name: str) -> str:
        """列名安全校验，支持汉字"""
        if not re.match(r"^[a-z_\u4e00-\u9fff][a-z0-9_\u4e00-\u9fff]*$", name, re.I):
            raise SecurityError(f"Invalid column name: {name}")
        return f'"{name}"'
