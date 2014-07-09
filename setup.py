from setuptools import setup, find_packages
from hiscore import __version__, __maintainer__, __email__

long_description = open('README.md').read()

install_requires = [
  'numpy',
  'gurobipy'
]

setup(
  name = 'hiscore',
  version = __version__,
  author = __maintainer__,
  author_email = __email__,
  packages = find_packages(),
  description = 'A simple and powerful scoring/ranking engine',
  long_description=long_description,
  install_requires=install_requires,
  url = 'https://github.com/aothman/hiscore', # use the URL to the github repo
  keywords = [],
  classifiers =[
    'Operating System :: OS Independent',
    'License :: OSI Approved :: GNU General Public License (GPL)'
  ],
)