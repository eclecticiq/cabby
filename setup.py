from setuptools import setup, find_packages

setup(
    name = "taxii_client",
    version = "0.0.1",

    packages = find_packages(),

    scripts = [
        '/bin/taxii-discovery'
        '/bin/taxii-poll'
        '/bin/taxii-push'
    ],

    install_requires = [
        'libtaxii'
    ]
)
