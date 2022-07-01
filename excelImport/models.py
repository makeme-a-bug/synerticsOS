from django.db import models

class ExcelFile(models.Model):
    file = models.FileField(upload_to='excel/')
    created = models.DateTimeField(auto_now_add=True)

    def delete(self, using=None, keep_parents=False):
        self.file.storage.delete(self.file.name)
        super().delete()