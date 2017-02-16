#!/usr/bin/env python
from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

setup(
    name='Flask-WXPay',
    version='0.1.0',
    description='Flask Extension for WeChat Pay.',
    long_description=readme,
    author='codeif',
    author_email='me@codeif.com',
    url='https://github.com/codeif/Flask-WXPay',
    license='MIT',
    install_requires=['requests', 'httpdns'],
    packages=find_packages(),
)
