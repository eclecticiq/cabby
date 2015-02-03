import os
from setuptools import setup, find_packages


def here(*path):
    return os.path.join(os.path.dirname(__file__), *path)

with open(here('README.rst')) as fp:
    long_description = fp.read()

setup(
    name="taxii-client",
    description="Client for interacting with TAXII servers",
    long_description=long_description,
    version="0.0.2",
    url="https://github.com/Intelworks/taxii-client/",
    author="Intelworks",
    author_email="development@intelworks.com",
    packages=find_packages(),
    scripts=[
        'bin/taxii-collections',
        'bin/taxii-discovery',
        'bin/taxii-poll',
        'bin/taxii-push',
    ],
    install_requires=[
        'libtaxii==1.1.105-SNAPSHOT',
        'pytz',
        'colorlog',
    ],
)
