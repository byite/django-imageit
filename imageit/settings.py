# Django library.
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def retrieve(name):
    try:
        return getattr(settings, name, False)
    except ImproperlyConfigured:
        # To handle the auto-generation of documentations.
        return False


IMAGEIT_MAX_UPLOAD_SIZE_MB = retrieve('IMAGEIT_MAX_UPLOAD_SIZE_MB') or 5
IMAGEIT_MAX_SAVE_SIZE_MB = retrieve('IMAGEIT_MAX_SAVE_SIZE_MB') or 5
IMAGEIT_ACCEPTED_CONTENT_TYPES = retrieve('IMAGEIT_ACCEPTED_CONTENT_TYPES') or 'image/jpeg', 'image/png', 'image/svg+xml'
IMAGEIT_SVG_CONTENT_TYPE = retrieve('IMAGEIT_SVG_CONTENT_TYPE') or 'image/svg+xml'
IMAGEIT_DPI = retrieve('IMAGEIT_DPI') or 90
IMAGEIT_DEFAULT_IMAGE_PROPS = retrieve('IMAGEIT_DEFAULT_IMAGE_PROPS') or {"max_width": 1000, "max_height": 1000, "quality": IMAGEIT_DPI, "upscale": False}
IMAGEIT_IMAGE_PROPERTIES = retrieve('IMAGEIT_IMAGE_PROPERTIES') or ['max_width', 'max_height', 'quality', 'upscale', 'max_save_size_mb']
IMAGEIT_CROP_PROPERTIES = retrieve('IMAGEIT_CROP_PROPERTIES') or ["x1", "y1", "x2", "y2"]