# Copyright (C) 2008-2010 INRIA - EDF R&D
# Author: Damien Garaud
#
# This file is part of the PuppetMaster project. It checks the module
# 'network'.
#
# This script is free; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.

import sys
import socket
import unittest

from puppetmaster import network


test_method_name = ['testInit', 'testGetValue', 'testUsedMemory',
                    'testAvailableHost', 'testLaunchCommand']


class NetworkTestCase(unittest.TestCase):

    def __init__(self, methodName='runTest', host_file = None,
                 forced_ssh_config = False):
        unittest.TestCase.__init__(self, methodName)
        self.host_file = host_file
        self.forced_ssh_config = forced_ssh_config
        # If there is file.
        if self.host_file == None:
            self.is_file = False
        else:
            self.is_file = True

    def setUp(self):
        import random
        if self.is_file:
            self.net = network.Network(self.host_file, self.forced_ssh_config)
        # Just local host.
        self.net_local = network.Network()
        # The command which will be launched.
        self.command = "echo 'Hello World!'"

    def tearDown(self):
        pass

    def testInit(self):
        # Checks the name and the number of cpu.
        # For the local host.
        self.assertTrue(self.net_local.hosts[0].name == socket.gethostname())
        self.assertTrue(self.net_local.GetNhost() == 1)
        self.assertTrue(self.net_local.hosts[0].connection)
        # Is there a file?
        if self.is_file:
            self.assertTrue(self.net.GetNhost() > 0)
            self.assertTrue(self.net.GetConnectedHostNumber() > 0)
        # Wrong argument.
        # An 'network' instance takes a list 'host' instance, list of string
        # or a file.
        self.assertRaises(ValueError, network.Network, 1)
        self.assertRaises(ValueError, network.Network, [])
        self.assertRaises(ValueError, network.Network, [1,2])
        self.assertRaises(ValueError, network.Network, 'no_file')

    def testGetValue(self):
        # For the local host.
        host_name = self.net_local.GetHostNames()
        proc_num = self.net_local.GetProcessorNumber()
        connected_num = self.net_local.GetConnectedHostNumber()
        # 'host_name' must be a list of string.
        self.assertTrue(isinstance(host_name, list))
        self.assertTrue(isinstance(host_name[0], str))
        # 'proc_num' must be a list of tuples (hostname, Nproc)
        self.assertTrue(isinstance(proc_num, list))
        self.assertTrue(isinstance(proc_num[0], tuple))
        self.assertTrue(isinstance(proc_num[0][0], str))
        self.assertTrue(isinstance(proc_num[0][1], int))
        # 'connected_num' must be an integer greater than 0.
        self.assertTrue(isinstance(connected_num, int))
        # Checks size.
        self.assertTrue(len(host_name) > 0)
        self.assertTrue(len(proc_num[0]) == 2)
        self.assertTrue(connected_num > 0)

        # For a list of hosts.
        if self.is_file:
            host_name = self.net.GetHostNames()
            proc_num = self.net.GetProcessorNumber()
            connected_num = self.net.GetConnectedHostNumber()
            # 'host_name' must be a list of string.
            self.assertTrue(isinstance(host_name, list))
            self.assertTrue(isinstance(host_name[0], str))
            # 'proc_num' must be a list of tuples (hostname, Nproc)
            self.assertTrue(isinstance(proc_num, list))
            self.assertTrue(isinstance(proc_num[0], tuple))
            self.assertTrue(isinstance(proc_num[0][0], str))
            self.assertTrue(isinstance(proc_num[0][1], int))
            # 'connected_num' must be an integer greater than 0.
            self.assertTrue(isinstance(connected_num, int))
            # Checks size.
            self.assertTrue(len(host_name) > 0)
            self.assertTrue(len(proc_num[0]) == 2)
            self.assertTrue(connected_num > 0)

    def testUsedMemory(self):
        # Gets used memory ('free' Unix command).
        # For the local host.
        used_mem = self.net_local.GetUsedMemory()
        # 'used_mem' must be a list of tuple (hostname, value).
        self.assertTrue(isinstance(used_mem, list))
        self.assertTrue(isinstance(used_mem[0], tuple))
        self.assertTrue(isinstance(used_mem[0][0], str))
        # Checks size.
        self.assertTrue(len(used_mem) == 1)
        self.assertTrue(len(used_mem[0]) == 2)

        # For a list of hosts.
        if self.is_file:
            used_mem = self.net.GetUsedMemory()
            # 'used_mem' must be a list of tuple (hostname, value).
            self.assertTrue(isinstance(used_mem, list))
            self.assertTrue(isinstance(used_mem[0], tuple))
            self.assertTrue(isinstance(used_mem[0][0], str))
            # Checks size.
            self.assertTrue(len(used_mem) >= 1)
            self.assertTrue(len(used_mem[0]) == 2)

    def testAvailableHost(self):
        # Gets available hosts (used 'uptime' Unix command).
        # For the local host.
        available_host = self.net_local.GetAvailableHosts()
        # 'available_host' must be a list of tuple (hostname, available_cpu).
        self.assertTrue(isinstance(available_host, list))
        if len(available_host) > 0:
            self.assertTrue(isinstance(available_host[0], tuple))
            self.assertTrue(isinstance(available_host[0][0], str))
            self.assertTrue(isinstance(available_host[0][1], int))

        # For a list of hosts.
        if self.is_file:
            available_host = self.net.GetAvailableHosts()
            # 'available_host' must be a list of tuple
            # (hostname, available_cpu).
            self.assertTrue(isinstance(available_host, list))
            if len(available_host) > 0:
                self.assertTrue(isinstance(available_host[0], tuple))
                self.assertTrue(isinstance(available_host[0][0], str))
                self.assertTrue(isinstance(available_host[0][1], int))

    def testLaunchCommand(self):
        import random
        # For the local host.
        status = self.net_local.LaunchInt(self.command)
        statusout = self.net_local.LaunchFG(self.command)
        popen4_instance = self.net_local.LaunchBG(self.command)
        subproc = self.net_local.LaunchSubProcess(self.command)
        wait_return = self.net_local.LaunchWait(self.command, 2., 0.2)
        # Checks type.
        self.assertTrue(isinstance(status, int))
        self.assertTrue(isinstance(statusout, tuple))
        self.assertTrue(isinstance(statusout[0], int))
        self.assertTrue(isinstance(wait_return, tuple))
        # The status must be '0'.
        self.assertTrue(status == 0)
        self.assertTrue(statusout[0] == 0)
        self.assertTrue(popen4_instance.wait() == 0)
        self.assertTrue(subproc.wait() == 0)
        self.assertTrue(wait_return[0] == 0)

        # For a random host.
        if self.is_file:
            index = random.randint(0, self.net.GetNhost() - 1)
            random_host = self.net.hosts[index]
            # Launches the command.
            status = self.net.LaunchInt(self.command + ' 2>/dev/null',
                                        random_host)
            statusout = self.net.LaunchFG(self.command, random_host)
            popen4_instance = self.net.LaunchBG(self.command, random_host)
            subproc = self.net.LaunchSubProcess(self.command, random_host)
            wait_return = self.net.LaunchWait(self.command, 2., 0.2,
                                              random_host)
            # Checks type.
            self.assertTrue(isinstance(status, int))
            self.assertTrue(isinstance(statusout, tuple))
            self.assertTrue(isinstance(statusout[0], int))
            self.assertTrue(isinstance(wait_return, tuple))
            # The status must be '0' if the connection dit not fail.
            if random_host.connection:
                self.assertTrue(status == 0)
                self.assertTrue(statusout[0] == 0)
                self.assertTrue(popen4_instance.wait() == 0)
                self.assertTrue(subproc.wait() == 0)
                self.assertTrue(wait_return[0] == 0)
            else:
                self.assertTrue(status != 0)
                self.assertTrue(statusout[0] != 0)
                self.assertTrue(popen4_instance.wait() != 0)
                self.assertTrue(subproc.wait() != 0)
                self.assertTrue(wait_return[0] != 0)

if __name__ == '__main__':
    unittest.main()
