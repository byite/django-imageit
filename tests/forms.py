from django import forms
from .models import TestScaleItModel, TestCropItModel

class TestScaleItForm(forms.ModelForm):
    class Meta:
        model = TestScaleItModel
        fields = ['name', 'image']

class TestCropItForm(forms.ModelForm):
    class Meta:
        model = TestCropItModel
        fields = ['name', 'image']