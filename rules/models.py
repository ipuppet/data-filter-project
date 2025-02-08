from django.db import models, transaction


class Field(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
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
    def create_with_conditions(self, name, description, conditions_data):
        with transaction.atomic():
            rule = self.create(name=name, description=description)
            print(conditions_data)
            for condition_data in conditions_data:
                Condition.objects.create(rule=rule, **condition_data)
        return rule

    def update_with_conditions(self, rule, name, description, conditions_data):
        with transaction.atomic():
            rule.name = name
            rule.description = description
            rule.save()

            rule.conditions.all().delete()
            for condition_data in conditions_data:
                Condition.objects.create(rule=rule, **condition_data)

        return rule


class Rule(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RuleManager()

    def __str__(self):
        return self.name


class Condition(models.Model):
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name="conditions")
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    operator = models.CharField(max_length=200)
    required = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.rule} - {self.field} - {self.operator} - {self.value}"
