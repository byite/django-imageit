# Create your models here.
from django.db.models import FileField
from django.utils.translation import gettext_lazy as _


from .fields import ScaleItImageFormField, CropItImageFormField
from .settings import (
    IMAGEIT_DEFAULT_IMAGE_PROPS,
    IMAGEIT_IMAGE_PROPERTIES,
)
from . import utils


class ScaleItImageField(FileField):
    description = _("Image field that scales to the bounds of max_height and max_width")

    def __init__(self, *args, **kwargs):
        # Dictionary containing propeties for cropping and or scaling image
        # max_width, max_height, quality, max_upload_size, crop_props (for crop field)
        self.img_props = dict(IMAGEIT_DEFAULT_IMAGE_PROPS)

        for key, val in list(kwargs.items()):
            if key.lower() in IMAGEIT_IMAGE_PROPERTIES:
                self.img_props[key.lower()] = kwargs.pop(key)
        super(ScaleItImageField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        # Update form field class used. Can also pass kwargs to form class from defaults
        defaults = {
            'form_class': ScaleItImageFormField,
        }
        defaults.update(kwargs)
        # for passing kwargs to form_class if required
        # defaults.update(**self.img_props)
        # Returns instantiated form_class class
        return super(ScaleItImageField, self).formfield(**defaults)

    # Required to reconstruct state of model field instance. 
    # (Any updated kwargs must be returned if varying from default value used in init)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.img_props != IMAGEIT_DEFAULT_IMAGE_PROPS:
            kwargs.update(self.img_props)
        return name, path, args, kwargs
    
    def _clean(self, value):
        scaled_img = utils.process_upload(value, self.img_props)
        scaled_img.cleaned = True
        return scaled_img

    # Returns a cleaned django InMemoryUploadedFile instance
    def clean(self, value, model_instance):
        scaled_img = self._clean(value)
        return super().clean(scaled_img, model_instance)

    # Scaling/Cropping and file Checks are verified in model as apposed to form,
    # ensuring files are always validated, even when adding programatically
    def pre_save(self, model_instance, add):
        file = getattr(model_instance, self.attname)

        # Prevents re-running of clean when using from form 
        # as form.post_clean triggers model clean methods
        if file and not hasattr(file, 'cleaned'):
            file.file = self._clean(file.file)
            setattr(model_instance, self.attname, file)
        return super().pre_save(model_instance, add)


class CropItImageField(ScaleItImageField):
    description = _("Image field that crops an image then scales it to the bounds of max_height and max_width")

    def formfield(self, **kwargs):
        defaults = {
            'form_class': CropItImageFormField,
        }
        defaults.update(kwargs)
        return super(CropItImageField, self).formfield(**defaults)

    # value: InMemoryUploadedFile
    def clean(self, value, model_instance):
        # Check to see if crop_props are present in file. 
        # (hasattr checks to avoid throwing attribute error (no file) on unchanged initial file (s3BotoFile))
        if hasattr(value, 'file') and hasattr(value.file, 'crop_props'):
            self.img_props.update({'crop_props': value.file.crop_props})

        return super().clean(value, model_instance)