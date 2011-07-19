#!/usr/bin/env python

from distutils.core import setup

setup(name='django-superadmin',
    version='0.1',
    description='Easy to install admin interface for your applications!',
    author='buriy',
    author_email='burchik@gmail.com',
    url='https://github.com/buriy/django-superadmin',
    packages=['superadmin', ],
    include_package_data = True,    # include everything in source control
    package_data={'superadmin': ['*.py','*/*.py', '*.txt','*.css','*.gif','js/*.js','templates/*.html']},
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        'Environment :: Web Environment',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        "Framework :: Django",
        ],
    long_description = """\
Easy to install admin interface for your applications!
"""
)
