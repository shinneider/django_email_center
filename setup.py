#!/usr/bin/env python

from io import open

from setuptools import find_packages, setup

from django_history.meta import VERSION

setup(
    name='django-email-center',
    version=str(VERSION),
    description='The "Django Email Center" is a solutions for send your email(s)',
    long_description=open('README.md', encoding='utf-8').read(),
    author='Shinneider Libanio da Silva',
    author_email='shinneider-libanio@hotmail.com',
    url='https://github.com/shinneider/django_email_center',
    license='MIT',
    packages=find_packages(exclude=('tests.*', 'tests', 'example')),
    install_requires=[
        # 'Django>=2.0',
        # 'Python>=3.5',
    ],
    include_package_data=True,
)