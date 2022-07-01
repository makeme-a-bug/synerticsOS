from django.contrib import admin
from . import models

admin.site.register(models.Order)
admin.site.register(models.Driver)
admin.site.register(models.Trip)