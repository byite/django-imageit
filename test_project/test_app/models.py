from django.db import models

from imageit.models import ScaleItImageField, CropItImageField
from imageit.widgets import ScaleItImageWidget, CropItImageWidget

class PhotoModel(models.Model):
    scale_photo = ScaleItImageField(null=True, blank=True)
    crop_it_photo = CropItImageField(null=True, blank=True)
