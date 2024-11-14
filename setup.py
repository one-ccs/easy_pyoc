#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='easy_pyoc',
    version='0.6.1',
    description='封装一些 Python 组件',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='one-ccs',
    author_email='one-ccs@foxmail.com',
    url='https://github.com/one-ccs/easy_pyoc',
    repository='https://github.com/one-ccs/easy_pyoc',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3',
    packages=find_packages(
        where='.',
        exclude=('test', ),
        include=('*', ),
    ),
    package_dir={},
    package_data={
        'easy_pyoc': ['qt5/res/**'],
    },
    exclude_package_data={},
    install_requires=[],
    extras_require={
        'easy_pyoc.qt5': ['PyQt5'],
        'utils.flask_util': ['flask'],
        'utils.yaml_util': ['PyYAML'],
    },
)
