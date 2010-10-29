.. _testing:

*******
Testing
*******

.. Line number in the interactive Python code-block (with '>>>') if the number
.. of lines exceeds 5.
.. .. highlight:: python
..    :linenothreshold: 5

In order to keep a code with well conventions and to check each source code modifications, two tools are used:

  - `Pylint`_
  - `unittest`_



Code Quality
============

`Pylint`_ is a useful tool which can analyze Python modules and send a report
with messages about errors, warnings, conventions and refactoring. It sends
stats and can compare the source code modifications with the previous analyze. It can send bug error messages without executing the code.

It is a good way to improve a code.
 
A Pylint configuration file ``.pylintrc`` was generated in the PuppetMaster
root directory. To launch Pylint to analyze the module ``host.py`` for
instance::

    $> pylint --rcfile=.pylintrc host.py

To avoid all stats tables::

    $> pylint --rcfile=.pylintrc -r n host.py


Unit Test
=========

The sub-directory ``test`` contains useful unit tests. You can use two scripts:

  - ``remote_hosts_test.py``
  - ``tests.py``

These scripts use the `unittest`_ Python module.

SSH connection checking
-----------------------

This script is used to check SSH connections of a remote hosts list. Write a
file with host names, ``my_host.txt`` for instance, and do::

    $> python remote_hosts_test.py my_host.txt

To force the PuppetMaster 's SSH configuration::

    $> python remote_hosts_test.py my_host.txt yes


Automatic tests
---------------

It is possible to launch several tests. You can launch all tests or a few
tests according to one module. To know the available options, do::

    $> python tests.py --help

Let ``host_list`` be a text file with the list of host names::

    $> python tests.py -f host_list

Launch tests for the module ``host.py``::

    $> python tests.py -f host_list -m host

To force PuppetMaster's SSH configuration and launch test for the module
``network``::

    $> python tests.py -f host_list --force-ssh-config -m network


.. _Pylint: http://www.logilab.org/project/pylint
.. _unittest: http://docs.python.org/library/unittest.html
