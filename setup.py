from setuptools import setup, find_packages

setup(
    name="taxii-client",
    version="0.0.2",
    url="https://github.com/Intelworks/taxii-client/",
    author="Intelworks",
    author_email="founders@intelworks.com",
    packages=find_packages(),
    scripts=[
        'bin/taxii-discovery',
        'bin/taxii-poll',
        'bin/taxii-push',
    ],
    install_requires=[
        'libtaxii==1.1.105-SNAPSHOT',
        'pytz',
        'colorlog',
    ]
)
