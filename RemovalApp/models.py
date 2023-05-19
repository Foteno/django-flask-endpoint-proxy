from django.db import models
from django.conf import settings

class Image(models.Model):
    image = models.ImageField(upload_to=settings.MEDIA_ROOT)