.. _quickstart:

**********
QuickStart
**********

.. Line number in the interactive Python code-block (with '>>>') if the number
.. of lines exceeds 5.
.. .. highlight:: python
..    :linenothreshold: 5

A quickstart with PuppetMaster.

.. _host:

Host
====

* Local Host

  Open an interactive Python window and do::
   
    >>> from puppetmaster.host import Host
    >>> host = Host()

  Per default, it takes the local host. Then you can test a few methods::

    >>> host.name
    'keyts'
    >>> host.connection
    True
    >>> host.GetProcessorNumber()
    2
    >>> host.GetUptime()
    [0.2, 0.12, 0.07]
    >>> host.GetTotalMemory()
    2035456


* Remote Host

  Suppose you have a remote host which is called ``whitman``. The connection
  with this host is done with SSH. Then, you can use the same methods as
  previously::
  
    >>> host = Host('whitman')
    >>> host.name
    'whitman'
    >>> host.connection
    True
    >>> host.GetProcessorNumber()
    4
    >>> host.GetUptime()
    [3.8, 3.7, 3.68]
    >>> host.GetTotalMemory()
    4025246

  If the SSH connection fails, the attribute ``connection`` is set to
  ``False``::

    >>> wrong_host = Host('fake')
    >>> wrong_host.connection
    False


.. _network:

Network
=======

  .. note::
     You must have a well configured SSH connection. Don't forget to launch
     ``ssh-add`` in order to avoid the pass-phrase for each connection to a
     specific host.

  You can create a file with the host names such as::

    keats
    whitman
    dickinson
    wilde
   
  This file is called ``host_list.txt`` for instance. Just do::
  
    >>> from puppetmaster.network import Network
    >>> net = Network('host_list.txt')

  to declare an instance ``Network``. As you use a SSH connection, may be you
  don't want to have this message when it is your first connection to a
  specific host::

    The authenticity of host 'wilde (172.22.XX.XX)' can't be established.
    RSA key fingerprint is dd:6e:1c:22:0b:a5:99:98:21:fd:57:08:ff:b7:1d:e5.
    Are you sure you want to continue connecting (yes/no)?

  In order to avoid this message, you can do::

    >>> net = Network('host_list.txt', forced_ssh_config=True)

  A PuppetMaster SSH configuration is used with the option
  ``StrictHostKeyChecking no`` and avoids the boring message.

  The approximately same methods are used for an instance ``Network`` as a
  single instance ``Host``. Note that the SSH requests to a group of hosts use
  the `threading <http://docs.python.org/library/threading.html>`_ Python
  module.

  Do::

    >>> net.GetProcessorNumber()
    [('keats', 3), ('whitman', 4), ('dickinson', 4), ('wilde', 8)]

  to have the CPUs number for each host.

  Maybe you would like to know the available host according to the number of
  cores for each host and the load averages. The following method return the
  names of available hosts and the number of programs that you can launch on
  it. It supposes that you have one program for one core.

    >>> net.GetAvailableHost()
    [('keats', 1), ('dickinson', 4), ('wilde', 6)]

  As you can see, ``whitman`` is too busy. You can launch several programs on
  the other remote hosts.
