import os
import glob
import uuid
from datetime import datetime
from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _


def upload_to(instance, filename):
    today = datetime.today().strftime("%Y/%m/%d")
    ext = filename.split(".")[-1]
    unique_filename = f"{instance.id}.{ext}"
    return os.path.join("uploads", today, unique_filename)


class File(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("File ID")
    )
    display_name = models.CharField(
        max_length=255, editable=False, verbose_name=_("Display name")
    )
    file = models.FileField(upload_to=upload_to, verbose_name=_("File"))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Upload time"))

    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _("Files")

    def get_full_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.file.path)

    def delete(self, *args, **kwargs):
        files = glob.glob(f"{self.get_full_path()}*")
        for file in files:
            os.remove(file)
        self.file.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.display_name or str(self.id)
