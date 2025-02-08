from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from .models import File
from .forms import FileForm
from .processor import FileConverter


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("id", "display_name", "uploaded_at")
    form = FileForm
    actions = ["process_file"]

    def delete_queryset(self, request, queryset):
        for file in queryset:
            file.delete()

    @admin.action(description="Process selected files")
    def process_file(self, request, queryset):
        i = 0
        for file in queryset:
            converter = FileConverter(file)
            if converter.is_processed:
                self.message_user(
                    request,
                    f"File {file.display_name} is already processed.",
                    messages.WARNING,
                )
                continue
            converter.convert()
            i += 1
        if i == 0:
            message = "No files were processed."
        else:
            message = (
                ngettext(
                    "%d file was successfully converted to SQLite.",
                    "%d files was successfully converted to SQLite.",
                    i,
                )
                % i
            )
        self.message_user(request, message, messages.SUCCESS)
