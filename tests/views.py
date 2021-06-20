from django.shortcuts import render
from django.views.generic import CreateView

from .models import TestScaleItModel, TestCropItModel

# Create your views here.
class TestScaleItView(CreateView):
    model = TestScaleItModel
    template_name = "test_view.html"
    fields = ['image']


class TestCropItView(CreateView):
    model = TestCropItModel
    template_name = "test_view.html"
    fields = ['image']