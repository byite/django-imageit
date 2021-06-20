from django.conf.urls import url
from django.urls import path

from .views import (
    TestScaleItView,
    TestCropItView
)


urlpatterns = [
    path('test/scale-it', TestScaleItView.as_view(), name='test-scale-it'),
    path('test/crop-it', TestCropItView.as_view(), name='test-crop-it'),
]
