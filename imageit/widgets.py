from django.core.exceptions import ImproperlyConfigured
from django.forms.widgets import MultiWidget, ClearableFileInput
from django.utils.translation import gettext_lazy as _


class ScaleItImageWidget(ClearableFileInput):
    template_name = 'imageit/widgets/scale_it_widget.html'
    initial_text = 'Current'

    def __init__(self, *args, **kwargs):
        if kwargs.get('multiple') == True:
            raise ImproperlyConfigured(_('Scaleit image widget does not support multi-file selectors'), code="Disallowed widget attrs")
        super(ScaleItImageWidget, self).__init__(*args, **kwargs)

    class Media:
        css = {"all": ('imageit/css/imageit.css',),}
        js = ('imageit/js/imageit.js',)


class CropItImageWidget(MultiWidget):
    template_name = 'imageit/widgets/crop_it_widget.html'

    def __init__(self, *args, **kwargs):
        if kwargs.get('multiple') == True:
            raise ImproperlyConfigured(_('Cropit image widget does not support multi-file selectors'), code="Disallowed widget attrs")
        super(CropItImageWidget, self).__init__(*args, **kwargs)

    def decompress(self, value):
        if value:
            return [value, 0, 0, 0, 0]
        return [None, 0, 0, 0, 0]

    class Media:
        css = {"all": ('imageit/css/imageit.css', 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.9/cropper.min.css'),}
        js = ('https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.9/cropper.min.js', '/static/imageit/js/imageit.js')