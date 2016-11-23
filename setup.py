import os
from setuptools import setup, find_packages

__version__ = None
exec(open('cabby/_version.py').read())


def here(*path):
    return os.path.join(os.path.dirname(__file__), *path)


def get_file_contents(filename):
    with open(here(filename)) as fp:
        return fp.read()


# This is a quick and dirty way to include everything from
# requirements.txt as package dependencies.
install_requires = get_file_contents('requirements.txt').split()

setup(
    name="cabby",
    description="TAXII client library",
    long_description=get_file_contents('README.rst'),
    url="https://github.com/EclecticIQ/cabby/",
    author="EclecticIQ",
    author_email="cabby@eclecticiq.com",
    version=__version__,
    license="BSD License",
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'taxii-proxy=cabby.cli:proxy_content',
            'taxii-poll=cabby.cli:poll_content',
            'taxii-push=cabby.cli:push_content',
            'taxii-discovery=cabby.cli:discover_services',
            'taxii-collections=cabby.cli:fetch_collections',
            'taxii-subscription=cabby.cli:manage_subscription',
        ]
    },
    install_requires=install_requires,
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
