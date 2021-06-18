from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='django-imageit',
    version='0.0.1',
    url="https://github.com/scott-j5/django-imageit",
    author="Scott James",
    author_email="scottjames@byitegroup.com",
    description="Image processing plugin built for Django",
    packages=['imageit', 'imageit.tests'],
    long_description=long_description,
    long_description_content_type="text/markdown",

    install_requires = [
        "django >= 3",
        "pillow > 8.0.0",
        "filetype > 1.0.0",
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT Licence',
        'Operating System :: OS Independant',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: JavaScript',
        'Framework :: Django :: 3.0',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Presentation',
    ],
    keywords='django images imageit image upload scale crop resize',
)