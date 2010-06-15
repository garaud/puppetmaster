.. _getting_started:


***************
Getting started
***************

.. _get_code:

Get Code
========

You can get the PuppetMaster's code via the `Gitorious web site
<http://gitorious.org>`_.

Then, you just do::

  ln -s /path/to/puppetmaster/src puppetmaster

in a directory which appears in your ``PYTHONPATH``.


.. _installation:

Installation
============

You may already have PuppetMaster installed -- you can check by doing::

  > python -c 'import puppetmaster'

You must not have an error message such as::

  ImportError: No module named puppetmaster


.. _quickstart:

QuickStart
==========

.. Line number in the interactive Python code-block (with '>>>') if the number
.. of lines exceeds 5.
.. .. highlight:: python
..    :linenothreshold: 5

1. Create a file with a list of host names such as::

     muadib
     irulan
     idaho
     gesserit

   
   This file is called ``host_list.txt`` for instance.
      

2. Open an interactive Python window and do::

     >>> import puppetmaster
     >>> host = puppetmaster.Host()

   Per default, it takes the local host. Then you can test a few methods::

     >>> host.name
     'muadib'
     >>> host.connection
     True
     >>> host.GetProcessorNumber()
     2
     >>> host.GetUptime()
     [0.2, 0.12, 0.07]
   
   You can also launch different programs via SSH with a ``Host`` instance::

     >>> host.LaunchInt('program')
