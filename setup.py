from setuptools import setup
from os import path
import codecs

here = path.abspath(path.dirname(__file__))

with codecs.open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='i2b2-import',
    version='1.6.3',
    zip_safe=False,
    url='https://github.com/LREN-CHUV/i2b2-import',
    description='Import data into an I2B2 DB schema',
    long_description=long_description,
    author='Mirco Nasuti',
    author_email='mirco.nasuti@chuv.ch',
    license='Apache 2.0',
    packages=['i2b2_import'],
    extras_require={
        'test': ['unittest', 'nose'],
    },
    install_requires=['apache-airflow==1.8.2',
                      'sqlalchemy>=1.1.9',
                      'psycopg2>=2.7.3',
                      'pandas',
                      'defusedxml',
                      'xlrd'],
    include_package_data=True,
    package_data={'': ['default_data/default_structures_mapping.csv']},
    classifiers=(
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: Unix',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    )
)
