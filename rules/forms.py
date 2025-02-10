from django import forms
from .models import ConditionGroup


class ConditionGroupForm(forms.ModelForm):
    class Meta:
        model = ConditionGroup
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 如果是编辑现有实例
        if self.instance and self.instance.id:
            # 过滤 parent_group，仅显示与当前 rule 相同的 ConditionGroup
            self.fields["parent_group"].queryset = ConditionGroup.objects.filter(
                rule=self.instance.rule
            ).exclude(id=self.instance.id)
        else:
            # 如果是创建新实例，默认不显示任何 parent_group
            self.fields["parent_group"].queryset = ConditionGroup.objects.none()
