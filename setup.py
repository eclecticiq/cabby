import os
from setuptools import setup, find_packages


def here(*path):
    return os.path.join(os.path.dirname(__file__), *path)

with open(here('README.rst')) as fp:
    long_description = fp.read()

setup(
    name = "taxii-client",
    description = "Client for interacting with TAXII servers",
    long_description = long_description,
    version = "0.0.3",
    url = "https://github.com/Intelworks/taxii-client/",
    author = "Intelworks",
    author_email = "development@intelworks.com",
    packages = find_packages(),
    entry_points = {
        'console_scripts' : [
            'taxii-poll = taxii_client.cli:poll_content',
            'taxii-push = taxii_client.cli:push_content',
            'taxii-discovery = taxii_client.cli:discover_services',
            'taxii-collections = taxii_client.cli:fetch_collections',
        ]
    },
    dependency_links = [
        'git+https://github.com/TAXIIProject/libtaxii.git#egg=libtaxii-1.1.106'
    ],
    install_requires = [
        'pytz==2014.10',
        'colorlog',
    ],
)
