from .models import Rule


class SQLBuilder:
    def __init__(self, rule: Rule):
        self.rule = rule
