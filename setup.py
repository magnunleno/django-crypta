#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of Django-Crypta.
#
# Django-Crypta is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Django-Crypta is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Django-Crypta.  If not, see <http://www.gnu.org/licenses/>.

import io

from setuptools import find_packages, setup

from crypta.utils.setuptools import find_package_data, get_requirements

version = __import__('crypta').__version__

with io.open('README.rst', encoding='utf-8') as readme:
    long_description = readme.read()

if __name__ == '__main__':
    setup(
        name='django-crypta',
        version=version,
        author='Magnun Leno',
        author_email='magnun.leno@gmail.com',
        description='A Django app to manage secrets (passwords and others'
        ' sensitive informations) that need to be stored on the web and shared'
        ' (or not).',
        long_description=long_description,
        url='http://github.com/magnunleno/django-crypta',
        keywords='django password encryption storage sharing vault secrets'
        ' api',
        setup_requires=['pytest-runner'],
        install_requires=get_requirements('dist'),
        classifiers=[
            'Development Status :: 1 - Planning',
            'Environment :: Web Environment',
            'Framework :: Django',
            'Framework :: Django :: 1.11',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Internet',
            'Topic :: Utilities',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'License :: OSI Approved :: GNU Lesser General Public License v3 '
            'or later (LGPLv3+)',
        ],
        packages=find_packages(exclude=[]),
        package_data=find_package_data(),
        include_package_data=True,
    )
