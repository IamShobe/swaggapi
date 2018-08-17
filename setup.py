"""Setup file for handling packaging and distribution."""
import sys

from setuptools import setup, find_packages

__version__ = "0.2.1"

requirements = [
    'django>=1.7,<1.8',
    ]

if not sys.platform.startswith("win32"):
    requirements.append('python-daemon')

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='swaggapi',
    version=__version__,
    description="Swagger REST API builder",
    long_description=long_description,
    license="MIT",
    author="Elran Shefer",
    author_email="elran777@gmail.com",
    install_requires=requirements,
    python_requires="~=2.7.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        ],
    )
