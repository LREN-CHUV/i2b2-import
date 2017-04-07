from setuptools import setup
from os import path
import codecs

here = path.abspath(path.dirname(__file__))

with codecs.open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='i2b2-import',
    version='1.5.7',
    url='https://github.com/LREN-CHUV/i2b2-import',
    description='Import data into an I2B2 DB schema',
    long_description=long_description,
    author='Mirco Nasuti',
    author_email='mirco.nasuti@chuv.ch',
    license='Apache 2.0',
    packages=['i2b2_import'],
    extras_require={
        'test': ['unittest'],
    },
    install_requires=['airflow', 'sqlalchemy', 'nose', 'psycopg2', 'pandas', 'defusedxml', 'xlrd']
)
