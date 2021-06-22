from django.core.exceptions import ImproperlyConfigured
from django.forms.widgets import MultiWidget, ClearableFileInput
from django.utils.translation import gettext_lazy as _

from .settings import (
    IMAGEIT_MAX_UPLOAD_SIZE_MB
)

class ScaleItImageWidget(ClearableFileInput):
    template_name = 'imageit/widgets/scale_it_widget.html'
    initial_text = 'Current'

    def __init__(self, *args, **kwargs):
        if kwargs.get('multiple') == True:
            raise ImproperlyConfigured(_('Scaleit image widget does not support multi-file selectors'), code="Disallowed widget attrs")
        super(ScaleItImageWidget, self).__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        if not attrs.get("data-max_upload_size"):
            attrs["data-max_upload_size"] = IMAGEIT_MAX_UPLOAD_SIZE_MB
        context = super().get_context(name, value, attrs)
        return context

    class Media:
        css = {"all": ('imageit/dist/css/imageit.css',),}
        js = ('imageit/dist/js/imageit.js',)


class CropItImageWidget(MultiWidget):
    template_name = 'imageit/widgets/crop_it_widget.html'

    def __init__(self, *args, **kwargs):
        if kwargs.get('multiple') == True:
            raise ImproperlyConfigured(_('Cropit image widget does not support multi-file selectors'), code="Disallowed widget attrs")
        super(CropItImageWidget, self).__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        if not attrs.get("data-max_upload_size"):
            attrs["data-max_upload_size"] = IMAGEIT_MAX_UPLOAD_SIZE_MB
        context = super().get_context(name, value, attrs)
        return context

    def decompress(self, value):
        if value:
            return [value, 0, 0, 0, 0]
        return [None, 0, 0, 0, 0]

    class Media:
        css = {"all": ('https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.9/cropper.min.css',),}
        js = ('https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.9/cropper.min.js',)