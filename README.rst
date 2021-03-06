
README for PuppetMaster
=======================

About
----- 

This project provides facilities to deal with computations on a GNU/Linux
network. You can know the load averages of multiple remote hosts and launch
several programs with it.


Requirements
------------

PuppetMaster should be compatible with python >= 2.5.

A well-configured SSH connection to reach the remote hosts that you want to
use.


Install
-------

Go to the root project directory and just do::

    python setup.py install

Maybe you need root permissions to do that. You can also decide to install
PuppetMaster in one of your own directory. Thus, you have to use the
``--prefix`` option. For instance::

    python setup.py install --prefix=$HOME/usr

PuppetMaster will be installed in
``$HOME/usr/lib/python2.x/site-packages``. You have to add this directory to
your environment variable ``PYTHONPATH`` if you want to import PuppetMaster.

See::

    python setup.py --help

for more information about Python package installation.

In order to check if PuppetMaster works, do::

    python -c 'import puppetmaster'

You must not have this message::

    Traceback (most recent call last):
    File "<string>", line 1, in <module>
    ImportError: No module named puppetmaster


Documentation
-------------

Look in the doc/ subdirectory.

Test
----

Look in the test/ subdirectory.


License
-------

This project is under GNU GPLv2. See the file COPYING.


Contacts
--------

Damien Garaud: damien.garaud@gmail.fr
