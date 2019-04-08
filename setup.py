"""Setup file for handling packaging and distribution."""
from __future__ import absolute_import
import sys

from setuptools import setup, find_packages

__version__ = "0.6.6"

requirements = [
    'django>=1.7,<1.9',
    'requests',
    'attrdict',
    'six'
]


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='swaggapi',
    version=__version__,
    description="Swagger REST API builder",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="MIT",
    author="Elran Shefer",
    author_email="elran777@gmail.com",
    install_requires=requirements,
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*",
    packages=find_packages("src"),
    package_dir={"": "src"},
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        ],
    )
