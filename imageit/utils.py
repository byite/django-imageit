import sys

from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.utils.translation import gettext_lazy as _
import filetype
from io import BytesIO
from os import SEEK_END
from PIL import Image
from re import search, IGNORECASE, MULTILINE
from xml.etree.ElementTree import fromstring

from .filetypes import svgType
from .settings import (
    IMAGEIT_DEFAULT_IMAGE_PROPS,
    IMAGEIT_ACCEPTED_CONTENT_TYPES,
    IMAGEIT_MAX_UPLOAD_SIZE_MB,
    IMAGEIT_MAX_SAVE_SIZE_MB,
    IMAGEIT_SVG_CONTENT_TYPE
)

# data: Django InMemoryUploadedFile Instance
# img_props : dict {max_width, max_height, upscale, crop_props(opt.):{}}
def process_upload(data, img_props=None):
    # Check to see if a file was uploaded
    if isinstance(data, File):
        # Add svg mime type matcher
        filetype.add_type(svgType())
        data.content_type = filetype.guess(data.read(256)).mime
        if data.content_type is None:
            raise ValidationError(_("Unable to derive the content type of the file submitted"), code='file_invalid')

        # Determine the size of the file
        if hasattr(data, 'size'):
            size = data.size
        if hasattr(data, 'tell') and hasattr(data, 'seek'):
            pos = data.tell()
            data.seek(0, SEEK_END)
            size = data.tell()
            data.seek(pos)
        else:
            raise AttributeError("Unable to determine the file's size.")

        # Check to make sure image is an accepted content type
        if data.content_type in IMAGEIT_ACCEPTED_CONTENT_TYPES:
            # If file size exceeds max allowed, Raise error. Else process Image
            if size > (IMAGEIT_MAX_UPLOAD_SIZE_MB * 1024 * 1024):
                raise ValidationError(_("Uploaded file exceeds maximum allowed size of %(size)sMB.") %{ 'size': IMAGEIT_MAX_UPLOAD_SIZE_MB}, code="file_invalid")
            else:
                # Process vector or raster depending on file type
                if data.content_type == IMAGEIT_SVG_CONTENT_TYPE:
                    data = process_vector(data)
                else:
                    data = process_raster(data, img_props)
                
                # Validate file size after resampling 
                if size > (img_props.get('max_save_size_mb', IMAGEIT_MAX_SAVE_SIZE_MB) * 1024 * 1024):
                    raise ValidationError(_("Uploaded file exceeds maximum allowed size of %(size)sMB.") %{ 'size': IMAGEIT_MAX_SAVE_SIZE_MB}, code="file_invalid")
        else:
            raise ValidationError(_("Unsupported image format. Must be one of %(opts)s") % { 'opts': IMAGEIT_ACCEPTED_CONTENT_TYPES}, code='file_invalid')
    else:
        raise ValidationError(_("Process Upload requires a valid django File instance. %(type)s") % { 'type': type(data)}, code='file_invalid')
    return data


def process_vector(image):
    # Image: Django File Instance
    if contains_javascript(image):
        raise ValidationError(_("File rejected: JavaScript was detected within the file."), code='file_invalid')
    return image


def process_raster(image, img_props=None):
    # Image: Django File Instance
    if img_props == None or len(img_props) == 0:
        img_props = IMAGEIT_DEFAULT_IMAGE_PROPS

    # Returns Django File Instance
    scaled_image = resize(image, img_props)
    return scaled_image


def contains_javascript(image):
    image.file.seek(0)
    file_str = str(image.file.read(), encoding='UTF-8')

    # Filters against "script" / "if (.)" / "for (.)".
    pattern = r'(?i)(<\s*\bscript\b.*>.*?)|(.*\bif\b\s*\(.?.*\))|(.*\bfor\b\s*\(.*\))'

    found = search(
        pattern=pattern,
        string=file_str,
        flags=IGNORECASE | MULTILINE
    )
    
    if found is not None:
        return True

    parsed_xml = (
        (attribute, value)
        for elm in fromstring(file_str).iter()
        for attribute, value in elm.attrib.items()
    )

    for key, val in parsed_xml:
        if '"' in val or "'" in val:
            return True

    return False


def resize(image, img_props):
    # Image: Django File Instance
    # Open image and store format/metadata.
    pil_image = Image.open(image)
    pil_image_format, pil_image_info = pil_image.format, pil_image.info
    if img_props.get('quality'):
        pil_image_info['quality'] = img_props.get('quality')

    # Force PIL to load image data.
    pil_image.load()

    #Retrieve Crop props
    crop_props = img_props.pop('crop_props', False)

    #Check that all required co-oords are present and valid
    if crop_props and all(x in crop_props for x in ("x1", "y1", "x2", "y2")):
        if crop_props.get('x1') - crop_props.get('x2') == 0 or crop_props.get('y1') - crop_props.get('y2') == 0:
            raise ValidationError(_("Cropped image (%(file)s) cannot have a width or height or zero!" % {'file': image.name}), code='crop_invalid')
        else:
            pil_image = crop(pil_image, crop_props)
    elif crop_props and any(x in crop_props for x in ("x1", "y1", "x2", "y2")):
        raise ValidationError(_("Incomplete Cooridinates for cropping were recieved! Requires: x1, y1, x2, y2"), code='missing_crop_values')
    pil_image = scale(pil_image, img_props)

    # Close image and replace format/metadata, as PIL blows this away.
    pil_image.format, pil_image.info = pil_image_format, pil_image_info

    #Save pil image back to bytesio file
    extension = image.content_type.split('/')[-1].upper()
    bytes_image = BytesIO()
    try:
        pil_image.save(bytes_image, extension)
        bytes_image.seek(0, SEEK_END)
    except Exception as e:
        raise ValidationError(_("Error: %(e)s. There may be an issue with your image file.") % { 'e': e })
    pil_image.close()
    image.file = bytes_image
    return image


def crop(image, props):
    # Image: PIL Image
    image_width, image_height = map(float, image.size)

    x1, y1, x2, y2 = (props.get('x1'), props.get('y1'), props.get('x2'), props.get('y2'),)
    # Check if image actually requires cropping
    if not((x1 == 0 and x2 == image_width) or (y1 == 0 and y2 == image_height)):
        box = [
            int(x1),
            int(y1),
            int(x2),
            int(y2)
        ]
        # Crop the image
        image = image.crop(box)
    return image


def scale(image, props):
    #Image: PIL Image

    max_width, max_height, upscale = (props.get('max_width'), props.get('max_height'), props.get('upscale'))
    image_width, image_height = map(float, image.size)

    #Calculate scale ratio ensuring no side is longer than max dimenstions
    ratio = min(max_width / image_width, max_height / image_height)

    # Scale image if image must be scaled down or if upscale is set to true
    if ratio < 1.0 or (ratio > 1.0 and upscale):
        scaled_width = image_width * ratio
        scaled_height = image_height * ratio
    
        image = image.resize(
            (int(scaled_width), int(scaled_height)),
            resample=Image.ANTIALIAS
        )
    return image
