from os.path import join, dirname
from setuptools import setup, find_packages

CURRENT_DIR = dirname(__file__)

def get_file_contents(filename):
    with open(join(CURRENT_DIR, filename)) as fp:
        return fp.read()

setup(
    name = "cabby",
    description = "Client for interacting with TAXII servers",
    long_description = get_file_contents('README.rst'),
    url = "https://github.com/Intelworks/cabby/",
    author = "Intelworks",
    author_email = "cabby@intelworks.com",
    version = "0.0.3",
    license = "BSD License",
    packages = find_packages(),
    entry_points = {
        'console_scripts' : [
            'taxii-poll = cabby.cli:poll_content',
            'taxii-push = cabby.cli:push_content',
            'taxii-discovery = cabby.cli:discover_services',
            'taxii-collections = cabby.cli:fetch_collections',
            'taxii-subscription = cabby.cli:manage_subscription',
        ]
    },
    dependency_links = [
        'git+https://github.com/TAXIIProject/libtaxii.git#egg=libtaxii-1.1.106a'
    ],
    install_requires = [
        'pytz==2014.10',
        'colorlog',
        'libtaxii==1.1.106a'
    ],
)
