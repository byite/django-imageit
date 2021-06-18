from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.files import File
from django.test import TestCase, modify_settings
from PIL import Image

from imageit.models import ScaleItImageField
from .models import TestScaleItModel, TestCropItModel
from .forms import TestScaleItForm, TestCropItForm


#sys.stderr.write(repr('') + '\n')

@modify_settings(INSTALLED_APPS={
    'append': 'imageit.tests',
})
class ScaleItModelFieldTestCase(TestCase):
    def setUp(self):
        with open('imageit/tests/static/img/test1000x1000.png', 'rb') as img:
            scaled_img = TestScaleItModel.objects.create(name='scaled_png', image=File(img))

        with open('imageit/tests/static/img/test1000x1000xxx.png', 'rb') as img:
            scaled_img = TestScaleItModel(name='scaled_png_saved', image=File(img))
            scaled_img.save()
        
        with open('imageit/tests/static/img/test_svg.svg', 'rb') as img:
            scaled_img = TestScaleItModel.objects.create(name='test_svg', image=File(img))

    def test_deconstruction(self):
        scale_it_model_field = ScaleItImageField(max_width=100, max_height=100, quality=100, null=True, blank=True)
        name, path, args, kwargs = scale_it_model_field.deconstruct()
        new_instance = ScaleItImageField(*args, **kwargs)
        self.assertEqual(scale_it_model_field.img_props, new_instance.img_props)

    def test_img_uploaded(self):
        img2 = TestScaleItModel.objects.get(name='test_svg').image
        self.assertNotEqual(img2, None)

    def test_raster_scaled(self):
        img1 = TestScaleItModel.objects.get(name='scaled_png').image
        with Image.open(img1) as img_open:
            self.assertEqual(img_open.size, (100,100))

    def test_raster_scaled_from_save(self):
        img1 = TestScaleItModel.objects.get(name='scaled_png_saved').image
        with Image.open(img1) as img_open:
            self.assertEqual(img_open.size, (100,100))

    def test_invalid_file(self):
        with self.assertRaises(ValidationError):
            with open('imageit/tests/static/docs/test.pdf', 'rb') as img:
                scaled_img = TestScaleItModel.objects.create(name='test4', image=File(img))
                scaled_img.save()

    def test_script_injection(self):
        with self.assertRaises(ValidationError):
            with open('imageit/tests/static/img/test_svg_js.svg', 'rb') as img:
                scaled_img = TestScaleItModel.objects.create(name='test5', image=File(img))
                scaled_img.save()


# Test Server side scaling of images
@modify_settings(INSTALLED_APPS={
    'append': 'imageit.tests',
})
class ScaleItFormFieldTestCase(TestCase):
    def setUp(self):
        with open('imageit/tests/static/img/test1000x1000.png', 'rb') as img:
            form = TestScaleItForm(data={"name": "test_form_field_scale"} , files={"image": File(img)})
            if form.is_valid():
                form.save()

        with open('imageit/tests/static/img/test1000x1000.png', 'rb') as img:
            form = TestScaleItForm(data={"name": "test_form_blank_input"} , files={"image": File(img)})
            if form.is_valid():
                form.save()

    def test_image_scaled_from_form(self):
        img = TestScaleItModel.objects.get(name="test_form_field_scale").image
        with Image.open(img.open()) as img_open:
            self.assertEqual(img_open.size, (100,100))

    def test_blank_input(self):
        img = TestScaleItModel.objects.get(name="test_form_blank_input")
        form = TestCropItForm(data={"image-clear": 'on'})
        form = TestCropItForm(data={"name": "test_crop" , 'image_1': '0', 'image_2': '0', 'image_3': '0', 'image_4': '0'}, files={"image_0": ''})
        form.instance = img
        if form.is_valid():
            form.save()
        self.assertEqual(img.image, form.instance.image)
    
    def test_clear_image(self):
        img = TestScaleItModel.objects.get(name="test_form_field_scale")
        form = TestCropItForm(data={"name": "test_crop" , "image_0-clear": 'on', 'image_1': '0', 'image_2': '0', 'image_3': '0', 'image_4': '0'}, files={"image_0": ''})
        
        form.instance = img
        if form.is_valid():
            form.save()
        with self.assertRaises(ObjectDoesNotExist):
            img = TestScaleItModel.objects.get(name="test_form_field_scale")

# Test Server side cropping of images
# Test Server side scaling of images
@modify_settings(INSTALLED_APPS={
    'append': 'imageit.tests',
})
class CropItTestCase(TestCase):
    def setUp(self):
        with open('imageit/tests/static/img/test1000x1000xxx.png', 'rb') as img:
            form = TestCropItForm(data={"name": "test_crop" , 'image_1': '10', 'image_2': '10', 'image_3': '100', 'image_4': '100'}, files={"image_0": File(img)})

            if form.is_valid():
                form.save()

    def test_image_cropped(self):
        img = TestCropItModel.objects.get(name="test_crop").image
        with Image.open(img.open()) as img_open:
            self.assertEqual(img_open.size, (90,90))

    def test_invalid_crop(self):
        with open('imageit/tests/static/img/test1000x1000xxx.png', 'rb') as img:
            form = TestCropItForm(data={"name": "test_invalid_crop" , 'image_1': '0', 'image_2': '0', 'image_3': '0', 'image_4': '0'}, files={"image_0": File(img)})

            try:
                if form.is_valid():
                    form.save()
            except ValidationError as e:
                self.assertEquals('crop_invalid', e.code)