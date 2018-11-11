#!/usr/bin/python3

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='linx_connection',
    version='0.0.2',
    author='Andrew Anderson',
    author_email='andrew-anderson.neo@yandex.ru',
    description='Module for talking to Arduino by serial port',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Mr-Andersen/LabWink',
    packages=setuptools.find_packages(),
    license='GNU GPL',
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: '
            'GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
    ),
    install_requires=['pyserial', 'ruamel.yaml']
)
