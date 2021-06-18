================
Django ImageIt
================

|PyPi_Version| |PyPi_Status| |Build_Status| |Format| |python_versions| |django_versions| |License|

Django ImageIt is a simple image handling plugin for Django that allows for scaling (&upscaling) and cropping of raster images. Imageit also has the capability to accept svg files if required.

Key features
============

* Preview current image and new image selected for upload.
* Scale images to fit the bounds of max_width and max_height.
* Crop images to user defined dimensions before being scaled.
* Option to upscale smaller images.
* Accepts .svg images.
* Django Admin support.


Documentation
=============
https://django-imageit.readthedocs.io/en/latest/


Usage
============
.. code-block:: shell

    pip install django-imageit

Add 'imageit to INSTALLED_APPS in your settings.py

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'imageit',
        ...
    ]

Import Imageit model fields as below to use them in your models. Both fields derive from the existing Django FileField meaning Imageit fields also accept the same kwargs as FileFields (such as upload_to).

.. code-block:: python

    from imageit.models import ScaleItImageField, CropItImageField

    class ImageItModel(models.Model):
        scale_image = ScaleItImageField(max_width=100, max_height=100, quality=100, null=True, blank=True)
        crop_image = ScaleItImageField(max_width=1000, max_height=1000, quality=100, null=True, blank=True)

If max_width, max_height or quality are not provided when instantiating the field, they will default to predefined values. If you wish to use your own custom defaults to override these, you can do so in your settings.py as follows:

.. code-block:: python

    IMAGEIT_MAX_UPLOAD_SIZE_MB = 5
    IMAGEIT_MAX_SAVE_SIZE_MB = 5
    IMAGEIT_DEFAULT_IMAGE_PROPS = {"max_width": 1000, "max_height": 1000, "quality": 100, "upscale": False}
    IMAGEIT_ACCEPTED_CONTENT_TYPES = retrieve('IMAGEIT_ACCEPTED_CONTENT_TYPES') or 'image/jpeg', 'image/png', 'image/svg+xml'
    IMAGEIT_SVG_CONTENT_TYPE = retrieve('IMAGEIT_SVG_CONTENT_TYPE') or 'image/svg+xml'

**IMAGEIT_MAX_UPLOAD_SIZE_MB** is provided in MB, and is validated on the client side as well as on the server before cropping/scaling.
**IMAGEIT_MAX_SAVE_SIZE_MB** is provided in MB, and is validated on the server after and scaling/cropping/resampling is completed.
**IMAGEIT_DEFAULT_IMAGE_PROPS** Default properties used to scale/resample images
**IMAGEIT_ACCEPTED_CONTENT_TYPES** Content types accepted by imageit. (File mimes are validated by 3rd party FileTypes package)

.. warning:: It is not reccomended to allow svg file uploads to untrusted users. Imageit will allow upload of svg images if specified in your accepted content types. It must be noted that while Imageit completes checks for scripts in svg files, no guarantee of security from XSS attacks is provided. 

.. _Django: https://www.djangoproject.com

.. |PyPi_Version| image:: https://img.shields.io/pypi/v/django-markdownx.svg
.. |PyPi_Status| image:: https://img.shields.io/pypi/status/django-markdownx.svg
.. |Build_Status| image:: https://img.shields.io/travis/neutronX/django-markdownx.svg
.. |Format| image:: https://img.shields.io/pypi/format/django-markdownx.svg
.. |python_versions| image:: https://img.shields.io/pypi/pyversions/django-markdownx.svg
.. |django_versions| image:: https://img.shields.io/badge/Django-2.0,%202.1,%202.2,%203.0-green.svg
.. |License| image:: https://img.shields.io/pypi/l/django-imageit.svg