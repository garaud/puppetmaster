#!/usr/bin/env python
# puppetmaster
"""Generic Setup script.

:copyright: 2009-2010 INRIA - EDF R&D.
:license: General Public License version 2 - http://www.gnu.org/licenses
"""

from distutils.core import setup

STD_BLACKLIST = ('.git', 'doc', 'build')
IGNORED_EXTENSIONS = ('.pyc', '.pyo', '.rst', '.txt', '~')

setup(name='puppetmaster',
      version='0.1',
      license='GPL',
      platforms='GNU/Linux',
      description='Linux network computation facilities',
      author='Damien Garaud',
      author_email='damien.garaud@gmail.com',
      url='http://gitorious.org/puppetmaster',
      download_url='http://gitorious.org/puppetmaster',
      package_dir={'puppetmaster': '.'},
      packages=['puppetmaster'],
      )
