from setuptools import setup, find_packages

__author__ = 'Abraham Othman'
__copyright__ = 'Copyright 2018, Abraham Othman'

__version__ = '1.6.0'
__maintainer__ = 'Abraham Othman'
__email__ = 'abrahamo@wharton.upenn.edu'

long_description = open('README.md').read()

install_requires = [
  'numpy',
  'cvxpy>=1.0.0',
  'cvxopt'
]

setup(
  name = 'hiscore',
  version = __version__,
  author = __maintainer__,
  author_email = __email__,
  packages = find_packages(),
  description = 'A simple and powerful engine for creating scores',
  long_description=long_description,
  install_requires=install_requires,
  url = 'https://github.com/aothman/hiscore', # use the URL to the github repo
  keywords = [],
  classifiers =[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3'
  ]
)
