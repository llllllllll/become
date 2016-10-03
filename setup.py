#!/usr/bin/env python
from setuptools import setup, Extension


with open('README.rst') as f:
    long_description = f.read()


setup(
    name='become',
    version='0.1.0',
    description='Make one object become another.',
    author='Joe Jevnik',
    author_email='joejev@gmail.com',
    packages=['become'],
    include_package_data=True,
    long_description=long_description,
    license='GPL-2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: C++',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
    url='https://github.com/llllllllll/become',
    ext_modules=[
        Extension(
            'become._become', [
                'become/_become.cc',
            ],
            libraries=['py'],
            language='C++',
            extra_compile_args=[
                '-Wall',
                '-Wextra',
                '-Wno-unused-parameter',
                '-Wno-missing-field-initializers',
                '-Wno-write-strings',
                '-std=gnu++14',
                '-O3',
            ],
        ),
    ],
)
