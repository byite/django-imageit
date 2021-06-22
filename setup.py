from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='django-imageit',
    version='0.0.5',
    url="https://github.com/byite/django-imageit",
    author="Scott James",
    author_email="scottjames@byitegroup.com",
    description="Image processing plugin built for Django",
    packages=['imageit'],
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/x-rst",

    install_requires = [
        "django >= 3",
        "pillow > 8.0.0",
        "filetype > 1.0.0",
    ],
    extras_require = {
        "dev": [
            "twine >= 3.4",
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: JavaScript',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Presentation',
    ],
    keywords='django images imageit image upload scale crop resize',
)