import os
import uuid
from datetime import datetime
from django.conf import settings
from django.db import models


def upload_to(instance, filename):
    today = datetime.today().strftime("%Y/%m/%d")
    ext = filename.split(".")[-1]
    unique_filename = f"{instance.id}.{ext}"
    return os.path.join("uploads", today, unique_filename)


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or str(self.id)

    def get_full_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.file.path)

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4()

        super().save(*args, **kwargs)
