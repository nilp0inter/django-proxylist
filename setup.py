from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='django-proxy',
      version=version,
      description="Proxy-list management application for Django.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='django proxy',
      author='Roberto Abdelkader Mart\xc3\xadnez P\xc3\xa9rez',
      author_email='robertomartinezp_gmail.com',
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
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
