.. PuppetMaster documentation master file, created by
   sphinx-quickstart on Tue Jun 15 15:56:35 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PuppetMaster's documentation!
========================================

Introduction
------------

Python version supported: 2.5, 2.6

With PuppetMaster, you can get some information on remote hosts and manage
it. Via a SSH connection and a few remote hosts, you can get the load averages
for each host and launch a list of commands: Unix commands, scripts, C++
compiled programs, ...

For instance, you have more than one hundred programs that you have to launch
on 16 hosts with 4 cores. PuppetMaster check the load averages on each host
according to the number of cores and will launch several programs via SSH on these hosts.

Suppose you need a configuration file for each program, you won't generate about hundred different configurations files. But you can write a generic one, called *template*, with keywords which will be replaced thanks to a dictionary.

PuppetMaster uses the modules `threading
<http://docs.python.org/library/threading.html>`_ and `subprocess
<http://docs.python.org/library/subprocess.html>`_ .

  - `threading <http://docs.python.org/library/threading.html>`_ is used to
    get some information faster: number of cores, load averages, ...
  - `subprocess <http://docs.python.org/library/subprocess.html>`_ is useful
    to launch programs in the background. These programs can be launched to
    the local host or to a remote host via SSH.


Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   getting_started.rst
   quickstart.rst
   testing.rst
   puppet_module.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
