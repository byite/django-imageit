from django.contrib.admin.widgets import AdminFileWidget
from django.core.validators import RegexValidator
from django.forms import MultiValueField, FileField, FloatField
from django.forms.widgets import HiddenInput

from .widgets import ScaleItImageWidget, CropItImageWidget


class ScaleItImageFormField(FileField):
    # Change widget to custom one
    widget = ScaleItImageWidget

    def __init__(self, widget=None, max_length=None, allow_empty_file=False, *args, **kwargs):
        # Stop Django admin from overriding widget with default AdminFileWidget
        # Occurs when instantiating widgets from admin views
        # See : https://github.com/django/django/blob/master/django/contrib/admin/options.py
        super(ScaleItImageFormField, self).__init__(*args, **kwargs)
        if isinstance(widget, AdminFileWidget):
            self.widget = ScaleItImageWidget

    def clean(self, data, initial=None):
        # If you want image in cleaned_data to be scaled/cropped
        # It must be completed here as model.clean is completed in form.post_clean
        # Img props will need to be passed from model.form_class
            # Should probably validate crop inputs here
        return super().clean(data, initial)

class CropItImageFormField(MultiValueField):
    widget = CropItImageWidget(widgets=[ScaleItImageWidget, HiddenInput, HiddenInput, HiddenInput, HiddenInput,])

    def __init__(self, max_length=None, widget=None, **kwargs):
        # Define one message for all fields.
        error_messages = {
            'incomplete': 'Missing values required for image crop (required: x, y, width, height).',
        }
        # Or define a different message for each field.
        fields = (
            ScaleItImageFormField(
                error_messages={'incomplete': 'Please select an image to upload.'},
                required=kwargs.get('required'),
            ),
            FloatField(
                error_messages={'incomplete': 'Please eneter a starting x value for image crop.'},
                validators=[RegexValidator(r'^[0-9]+.[0-9]+$', 'Please eneter an x1 value for image crop.')],
                required=True,
            ),
            FloatField(
                validators=[RegexValidator(r'^[0-9]+.[0-9]+$', 'Please eneter a y1 value for image crop.')],
                required=True,
            ),
            FloatField(
                validators=[RegexValidator(r'^[0-9]+.[0-9]+$', 'Please eneter an x2 value for image crop.')],
                required=True,
            ),
            FloatField(
                validators=[RegexValidator(r'^[0-9]+.[0-9]+$', 'Please eneter a y2 value for image crop.')],
                required=True,
            ),
        )
        super(CropItImageFormField, self).__init__(
            error_messages=error_messages, fields=fields,
            require_all_fields=False, **kwargs
        )


    # Compresses inputs into single file object with crop values as properties
    # data_list: list of all cleaned input values
    def compress(self, data_list):
        img = data_list[0]
        if img is not None and img is not False:
            img.crop_props = {"x1": data_list[1], "y1": data_list[2],"x2": data_list[3], "y2": data_list[4]}
        return img