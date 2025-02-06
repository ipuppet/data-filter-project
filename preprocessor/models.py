import os
import uuid
from datetime import datetime
from django.db import models


def upload_to(instance, filename):
    today = datetime.today().strftime("%Y/%m/%d")
    ext = filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    return os.path.join("uploads", today, unique_filename)


class File(models.Model):
    name = models.CharField(max_length=50, unique=True)
    file = models.FileField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        try:
            existing_file = File.objects.get(name=self.name)
            if existing_file.file and existing_file.file.path != self.file.path:
                existing_file.file.delete(save=False)
                existing_file.delete()
        except File.DoesNotExist:
            pass

        super().save(*args, **kwargs)
