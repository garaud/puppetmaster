.. _getting_started:

***************
Getting started
***************

.. _get_code:

Get Code
========

You can get the PuppetMaster's code via the `Gitorious web site
<http://gitorious.org/puppetmaster>`_. You can just do::

    $> git git://gitorious.org/puppetmaster/src.git puppetmaster

or::

    $> git http://git.gitorious.org/puppetmaster/src.git puppetmaster

.. _install:

Install
=======

Go to the ``puppetmaster`` directory and install it::

    $> python setup.py install

or::

    $> python setup.py install --prefix=$HOME/usr

for instance if you don't have root permissions. Don't forget to add the path
``$HOME/usr/lib/python2.x/site-packages`` to your environment variable
``PYTHONPATH``. Read the `official documentation`_ about this variable.

.. _official documentation: http://docs.python.org/using/cmdline.html#environment-variables


.. _checking:

Checking
========

You can check the installation with::

  $> python -c 'import puppetmaster'

You must not have an error message such as::

  ImportError: No module named puppetmaster
