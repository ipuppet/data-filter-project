from django.contrib import admin
from .models import File
from .forms import FileForm


class FileAdmin(admin.ModelAdmin):
    list_display = ("id", "display_name", "uploaded_at")
    form = FileForm

    def delete_queryset(self, request, queryset):
        for file in queryset:
            file.delete()


admin.site.register(File, FileAdmin)
