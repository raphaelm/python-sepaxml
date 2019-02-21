from codecs import open
from os import path

from setuptools import find_packages, setup

from sepaxml import version

here = path.abspath(path.dirname(__file__))

try:
    # Get the long description from the relevant file
    with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = ''

setup(
    name='sepaxml',
    version=version,
    description='Python SEPA XML implementations',
    long_description=long_description,
    url='https://github.com/raphaelm/python-sepaxml',
    author='Raphael Michel',
    author_email='mail@raphaelmichel.de',
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='xml banking sepa',
    install_requires=[
        'xmlschema',
        'text-unidecode'
    ],

    include_package_data=True,
    packages=find_packages(include=['sepaxml', 'sepaxml.*', 'sepadd', 'sepadd.*']),
)
