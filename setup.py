#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='oc-pytools',
    version='0.1.0',
    description='封装一些 Python 组件',
    author='one-ccs',
    author_email='one-ccs@foxmail.com',
    url='https://github.com/one-ccs/pyoc',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3',
    packages=find_packages(),
    package_data={
        'qt5': ['qt5/res/**'],
    },
    exclude_package_data={},
    install_requires=[],
    extras_require={
        'qt5': ['PyQt5'],
    },
)
