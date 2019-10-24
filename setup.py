from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'VERSION')) as f:
    version = f.read().strip()

install_requires = [
    'Django>=2.2.3',
    'SQLAlchemy==1.2',
    'boto==2.48.0',
    'dj-database-url>=0.4.0',
    'django-cors-headers>=3.0.2',
    'django-compressor>=2.3',
    'django-pipeline>=1.6.14',
    'django-sass-processor>=0.7.1',
    'ecdsa>=0.13',
    'futures>=3.1.1',
    'libsass>=0.13.3',
    'paramiko>=1.12.3,<2',
    'psycopg2-binary>=2.5.2',
    'requests>=2.18.4',
    'unicodecsv>=0.14.1',
    'whitenoise>=3.3.1'
]

setup(
    name='wazimap',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,

    description='A Django application for exploring census and other place-specific data',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/OpenUpSA/wazimap',

    # Author details
    author='OpenUp',
    author_email='greg@openup.org.za',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    include_package_data=True,

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=install_requires,

    setup_requires=[
        "setuptools_git >= 1.0",
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['nose', 'flake8'],
        'test': ['nose', 'flake8'],
        'gdal': ['GDAL', 'Shapely>=1.5.13'],
    },
)
