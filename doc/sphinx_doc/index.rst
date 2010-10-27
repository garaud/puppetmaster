.. PuppetMaster documentation master file, created by
   sphinx-quickstart on Tue Jun 15 15:56:35 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PuppetMaster's documentation!
========================================

Introduction
------------

Python version supported: 2.5

Not tested for newer Python versions.

With PuppetMaster, you can get some information on remote hosts and manage it. Via a SSH connection and a few remote hosts, you can get the load averages for each host and launch a list of commands: Unix commands, scripts, C++ executables, ...

It uses the modules `threading <http://docs.python.org/library/threading.html>`_ and `subprocess <http://docs.python.org/library/subprocess.html>`_ .

  - `threading <http://docs.python.org/library/threading.html>`_ is used to
    get some information faster.
  - `subprocess <http://docs.python.org/library/subprocess.html>`_ is useful
    to launch programs in the background. These programs can be launched to
    the local host or to a remote host via SSH.


Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   getting_started.rst
   quickstart.rst
   puppet_module.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

