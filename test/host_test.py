# Copyright (C) 2008-2010 INRIA - EDF R&D
# Author: Damien Garaud
#
# This file is part of the PuppetMaster project. It checks the module
# 'host'.
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
import unittest

from puppetmaster import host

test_method_name = ['testInit', 'testUptime', 'testUsedMemory',
                    'testLaunchCommand']


class HostTestCase(unittest.TestCase):

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
            f = open(self.host_file, 'r')
            output = f.readlines()
            f.close()
            # A list of host names.
            self.host_list_name = []
            for name in output:
                name = name.strip('\n')
                if len(name) != 0:
                    self.host_list_name.append(name)
        # The local host.
        self.local_host = host.Host()
        # A fake host.
        self.fake_host = host.Host('fake', self.forced_ssh_config)
        # Is there a file?
        if self.is_file:
            # Random host.
            index = random.randint(0, len(self.host_list_name) - 1)
            self.random_host = host.Host(self.host_list_name[index],
                                         self.forced_ssh_config)
        # The command which will be launched.
        self.command = "echo 'Hello World!'"

    def tearDown(self):
        pass

    def testInit(self):
        # Checks the name and the number of cpu.
        # For the local host.
        self.assertTrue(len(self.local_host.name) != 0)
        self.assertTrue(isinstance(self.local_host.GetProcessorNumber(), int))
        self.assertTrue(self.local_host.GetProcessorNumber() > 0)
        # For the fake host.
        self.assertTrue(len(self.fake_host.name) != 0)
        self.assertTrue(isinstance(self.fake_host.GetProcessorNumber(), int))
        self.assertTrue(not self.fake_host.GetProcessorNumber == 0)
        # For the random host.
        if self.is_file:
            self.assertTrue(len(self.random_host.name) != 0)
            proc_num = self.random_host.GetProcessorNumber()
            if self.random_host.connection:
                self.assertTrue(isinstance(proc_num, int))
                self.assertTrue(proc_num > 0)
        # Wrong argument.
        # A 'Host' instance takes a string, a tuple or a list.
        self.assertRaises(ValueError, host.Host, 1)
        self.assertRaises(ValueError, host.Host, (1,2,3))
        self.assertRaises(ValueError, host.Host, (1,2))
        self.assertRaises(ValueError, host.Host, ('host',-6))
        self.assertRaises(ValueError, host.Host, [])
        self.assertRaises(ValueError, host.Host, [1,2])
        self.assertRaises(ValueError, host.Host, ['host',-6])

    def testUptime(self):
        # Gets load averages ('uptime' Unix command).
        # For the local host.
        load_average = self.local_host.GetUptime()
        self.assertTrue(isinstance(load_average, list))
        self.assertTrue(load_average != 'off')
        self.assertTrue(len(load_average) == 3)
        self.assertTrue(self.local_host.connection)

        # For the fake host.
        load_average = self.fake_host.GetUptime()
        self.assertTrue(isinstance(load_average, str))
        self.assertTrue(load_average == 'off')
        self.assertTrue(not self.fake_host.connection)

        # For the random host.
        if self.is_file:
            load_average = self.random_host.GetUptime()
            # Does random host connection work?
            if self.random_host.connection:
                self.assertTrue(isinstance(load_average, list))
                self.assertTrue(load_average != 'off')
                self.assertTrue(len(load_average) == 3)
            else:
                self.assertTrue(isinstance(load_average, str))
                self.assertTrue(load_average == 'off')

    def testUsedMemory(self):
        # Gets used memory ('free' Unix command).
        # For the local host.
        used_mem = self.local_host.GetUsedMemory()
        self.assertTrue(isinstance(used_mem, int))
        self.assertTrue(used_mem != 'off')
        self.assertTrue(self.local_host.connection)

        # For the fake host.
        used_mem = self.fake_host.GetUsedMemory()
        self.assertTrue(isinstance(used_mem, str))
        self.assertTrue(used_mem == 'off')
        self.assertTrue(not self.fake_host.connection)

        # For the random host.
        if self.is_file:
            used_mem = self.random_host.GetUsedMemory()
            # Does random host connection work?
            if self.random_host.connection:
                self.assertTrue(isinstance(used_mem, int))
                self.assertTrue(used_mem != 'off')
            else:
                self.assertTrue(isinstance(used_mem, str))
                self.assertTrue(used_mem == 'off')

    def testLaunchCommand(self):
        # For the local host.
        sys_code = self.local_host.LaunchInt(self.command + ' &>/dev/null')
        statusout = self.local_host.LaunchFG(self.command)
        subproc = self.local_host.LaunchSubProcess(self.command)
        wait_output = self.local_host.LaunchWait(self.command, ltime = 0.5,
                                                 wait = 0.2)
        # Checks type.
        self.assertTrue(isinstance(sys_code, int))
        self.assertTrue(isinstance(statusout, tuple))
        self.assertTrue(isinstance(wait_output, tuple))
        # Checks status.
        self.assertTrue(sys_code == 0)
        self.assertTrue(statusout[0] == 0)
        self.assertTrue(subproc.wait() == 0)
        self.assertTrue(wait_output[0] == 0)

        # For the fake host.
        sys_code = self.fake_host.LaunchInt(self.command + ' 2>/dev/null')
        statusout = self.fake_host.LaunchFG(self.command)
        subproc = self.fake_host.LaunchSubProcess(self.command)
        wait_output = self.fake_host.LaunchWait(self.command, ltime = 0.5,
                                                wait = 0.2)
        # Checks type.
        self.assertTrue(isinstance(sys_code, int))
        self.assertTrue(isinstance(statusout, tuple))
        self.assertTrue(isinstance(wait_output, tuple))
        # Checks status.
        self.assertTrue(sys_code != 0)
        self.assertTrue(statusout[0] != 0)
        self.assertTrue(subproc.wait() != 0)
        self.assertTrue(wait_output[0] != 0)

        # For the random host.
        if self.is_file:
            sys_code = self.random_host.LaunchInt(self.command
                                                  + ' &>/dev/null')
            statusout = self.random_host.LaunchFG(self.command)
            subproc = self.random_host.LaunchSubProcess(self.command)
            wait_output = self.random_host.LaunchWait(self.command,
                                                      ltime = 0.5,
                                                      wait = 0.2)
            self.assertTrue(isinstance(sys_code, int))
            self.assertTrue(isinstance(statusout, tuple))
            self.assertTrue(isinstance(wait_output, tuple))
            # Does random host connection work?
            if self.random_host.connection:
                self.assertTrue(sys_code == 0)
                self.assertTrue(statusout[0] == 0)
                self.assertTrue(subproc.wait() == 0)
                self.assertTrue(wait_output[0] == 0)
            else:
                self.assertTrue(sys_code != 0)
                self.assertTrue(statusout[0] != 0)
                self.assertTrue(subproc.wait() != 0)
                self.assertTrue(wait_output[0] != 0)

if __name__ == '__main__':
    unittest.main()
