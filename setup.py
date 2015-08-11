from os.path import join, dirname
from setuptools import setup, find_packages

__version__ = None
exec(open('cabby/_version.py').read())

CURRENT_DIR = dirname(__file__)


def get_file_contents(filename):
    with open(join(CURRENT_DIR, filename)) as fp:
        return fp.read()

setup(
    name="cabby",
    description="Python library for interacting with TAXII servers",
    long_description=get_file_contents('README.rst'),
    url="https://github.com/Intelworks/cabby/",
    author="Intelworks",
    author_email="cabby@intelworks.com",
    version=__version__,
    license="BSD License",
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'taxii-poll=cabby.cli:poll_content',
            'taxii-push=cabby.cli:push_content',
            'taxii-discovery=cabby.cli:discover_services',
            'taxii-collections=cabby.cli:fetch_collections',
            'taxii-subscription=cabby.cli:manage_subscription',
        ]
    },
    install_requires=[
        'pytz',
        'colorlog',
        'libtaxii>=1.1.107',
        'furl==0.4.7',
        'requests==2.7.0'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Topic :: Internet",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
