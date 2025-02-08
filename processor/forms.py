from django import forms
from .models import File


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ["file"]

    def save(self, commit=True):
        instance = super().save(commit=False)
        if "file" in self.cleaned_data:
            instance.display_name = self.cleaned_data["file"].name
        if commit:
            instance.save()
        return instance
