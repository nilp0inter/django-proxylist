#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2012 Roberto Abdelkader Martínez Pérez
# 
# This file is part of Django-ProxyList.
# 
# Django-ProxyList is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Django-ProxyList is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Django-ProxyList.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(name='django-proxylist',
      version=version,
      description='Proxy-list management application for Django',
      long_description=open('README.txt').read(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Framework :: Django',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python',
          'Topic :: Internet :: Proxy Servers',
          ], 
      keywords='django proxylist',
      author='Roberto Abdelkader Mart\xc3\xadnez P\xc3\xa9rez',
      author_email='robertomartinezp@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'django-countries',
          'pycurl',
          'pygeoip',
          'django-celery',
          # -*- Extra requirements: -*-
          ],
      )
