# Copyright (C) 2008-2009 EDF R&D
# Author: Damien Garaud
#
# This file provides to check the module 'network' and 'program_manager'.
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

import os, sys
import unittest
sys.path.insert(0, '../')
import network
import program_manager
sys.path.pop(0)


###################
# GLOBAL VAIRABLE #
###################

configuration_file = '../example/example.cfg'
configuration_file = os.path.abspath(configuration_file)


#############
# HOST TEST #
#############

class HostTestCase(unittest.TestCase):

    def setUp(self):
        import random
        # The local host.
        self.local_host = network.Host()
        # A random host.
        self.network = network.Network()
        index_host = random.randint(0, len(self.network.hosts) - 1)
        self.remote_host = network.Host(self.network.hosts[index_host].name)
        # The command which will be launched.
        self.command = "echo 'Hello World!'"

    def tearDown(self):
        pass

    def testInit(self):
        self.assert_(len(self.local_host.name) != 0)
        self.assert_(not self.local_host.cpu <= 0)
        
    def testProcessingMethods(self):
        import time, popen2
        # Gets load averages.
        load_average = self.local_host.LoadAverage()
        self.assert_(not 9999 in load_average)
        load_average = self.remote_host.LoadAverage()
        self.assert_(not 9999 in load_average)
        load_avr_file = self.local_host.LoadAverageFile()
        self.assert_(os.path.isfile(load_avr_file))
        os.remove(load_avr_file)
        # Launches a command.
        self.local_host.LaunchInt(self.command)
        self.local_host.LaunchInt(self.command)
        out = self.local_host.LaunchFG(self.command)
        self.assert_(isinstance(out, tuple))
        self.assert_(out[0] == 0)
        out = self.local_host.LaunchBG(self.command)
        self.assert_(isinstance(out, popen2.Popen4))
        while (out.poll() == -1):
            time.sleep(0.1)
        self.assert_(out.poll() == 0)
        out = self.local_host.LaunchWait(self.command, ltime = 0.5, wait = 0.2)
        self.assert_(isinstance(out, tuple))
        self.assert_(out[0] == 0)


################
# NETWORK TEST #
################

class NetworkTestCase(unittest.TestCase):

    def setUp(self):
        self.host = network.Host()
        self.network = network.Network()
        # The command which will be launched.
        self.command = "echo 'Hello World!'"
        # For the mail.
        self.subject = "[network.py]: Test"
        self.message = "This is just a test."
    
    def tearDown(self):
        pass

    def testInit(self):
        self.assert_(len(self.network.hosts) > 0)
        load_averaged = self.network.GetLoadAverages()
        available_hosts = self.network.GetAvailableHosts()

    def testFunctions(self):
        self.assert_(network.IsNum('3.14'))
        self.assert_(not network.IsNum('pi'))
        self.assert_(network.IsInt('1'))
        self.assert_(not network.IsInt('3.14'))
        self.assert_(isinstance(network.ToNum('1'), int))
        self.assert_(isinstance(network.ToNum('3.14'), float))
        # Exceptions.
        self.assertRaises(Exception, network.ToNum, 'pi')
        self.assertRaises(ValueError, network.remove, 3.14)

    def testAccessMethods(self):
        # Prints host names (without Exceptions).
        # self.network.PrintHostNames()
        # Gets host names in a list.
        host_name_list = self.network.GetHostNames()
        self.assert_(isinstance(host_name_list, list))
        Nhost = len(host_name_list)
        self.assert_(Nhost != 0)
        # Gets load averages.
        load_averages = self.network.GetLoadAverages()
        self.assert_(isinstance(load_averages, list))
        self.assert_(len(load_averages) == Nhost)
        self.assert_(isinstance(load_averages[0], tuple))
        # Gets an available hosts.
        host_name = self.network.GetAvailableHost(load_limit = 0.3)
        self.assert_(host_name in host_name_list)
        # Gets available hosts.
        available_hosts = self.network.GetAvailableHosts()
        self.assert_(len(available_hosts) <= Nhost)
        self.assert_(isinstance(available_hosts, list))

    def testProcessingMethods(self):
        import random, time, popen2
        # List of hosts.
        host_name_list = self.network.GetHostNames()
        Nhost = len(host_name_list)
        # Launches a simple command in interactive mode.
        out = self.network.LaunchInt(self.command)
        self.assert_(out == 0)
        # Launches a simple command to a random host in interactive mode.
        host_index = random.randint(0, Nhost - 1)
        out = self.network.LaunchInt(self.command,
                                     host_name_list[host_index])
        self.assert_(out == 0)
        # Launches a simple command in the foreground.
        out = self.network.LaunchFG(self.command)
        self.assert_(isinstance(out, tuple))
        self.assert_(out[0] == 0)
        # Launches a simple command to a random host in the foreground.
        host_index = random.randint(0, Nhost - 1)
        out = self.network.LaunchFG(self.command,
                                    host_name_list[host_index])
        self.assert_(isinstance(out, tuple))
        self.assert_(out[0] == 0)
        # Launches a simple command in the foreground and waits.
        out = self.network.LaunchWait(self.command, ltime = 0.5)
        self.assert_(isinstance(out, tuple))
        self.assert_(out[0] == 0)
        # Launches a simple command in the background.
        out = self.network.LaunchBG(self.command)
        self.assert_(isinstance(out, popen2.Popen4))
        
        self.assert_(out.poll() == 0 or out.poll() == -1)
        # Launches a simple command to a random host in the background.
        host_index = random.randint(0, Nhost - 1)
        out = self.network.LaunchBG(self.command,
                                    host_name_list[host_index])
        self.assert_(isinstance(out, popen2.Popen4))
        while (out.poll() == -1):
            time.sleep(0.1)
        self.assert_(out.poll() == 0)
        # Launches a simple command in a screen.
        self.network.LaunchScreen(self.command)
        # Launches a simple command to a random host in a screen.
        host_index = random.randint(0, Nhost - 1)
        self.network.LaunchScreen(self.command,
                                  host_name_list[host_index])
        # Sends a mail.
        # self.network.SendMail(self.subject,
        #                       'login@domain.com',
        #                       'login@domain.com', self.message)
        # self.network.SendMailAttach(self.subject, '/etc/version',
        #                             'login@domain.com',
        #                             'login@domain.com', self.message)


###################
# PROGRAM MANAGER #
###################

class ProgramManagerTestCase(unittest.TestCase):

    def setUp(self):
        count = 0
        self.delay = 2.
        self.program_manager = program_manager.ProgramManager()
        self.program_list = ['/bin/ps', '/bin/ls', '/bin/pwd']
        for p in self.program_list:
            prg = program_manager.Program(name = p, group = count)
            self.program_manager.AddProgram(prg)
            count += 1
    
    def tearDown(self):
        pass

    def testInit(self):
        ensemble_program = program_manager.ProgramManager()
        # Raises an exception if the program list is empty.
        self.assertRaises(Exception, ensemble_program.Run)
        self.assertRaises(Exception, ensemble_program.RunNetwork)

    def testAccessMethods(self):
        log = self.program_manager.GetLog()
        self.assert_(isinstance(log, str))

    def testProcessingMethods(self):
        self.program_manager.Try()
        self.program_manager.Run()
        self.program_manager.RunNetwork(self.delay)
        self.program_manager.Clear()
        self.assert_(len(self.program_manager.program_list) == 0)
        

class ProgramTestCase(unittest.TestCase):

    def setUp(self):
        self.command_name = '/bin/ls'
        self.program = program_manager.Program(self.command_name)
    
    def tearDown(self):
        pass

    def testInit(self):
        pass

    def testAccessMethods(self):
        command_name = self.program.Command()
        self.assert_(isinstance(command_name, str))

    def testProcessingMethods(self):
        self.assert_(self.program.IsReady())
        self.program.Try()
        self.program.Run()


class ConfigurationTestCase(unittest.TestCase):

    def setUp(self):
        self.config = program_manager.Configuration(configuration_file)
        
    def tearDown(self):
        pass

    def testInit(self):
        pass

    def testAccessMethods(self):
        replacement = self.config.GetReplacementMap()

    def testProcessingMethods(self):
        import pwd, socket, time, platform
        current_date = time.asctime()
        username = pwd.getpwuid(os.getuid())[0]
        computer = socket.gethostname()
        tmp = platform.dist()
        distribution = tmp[0] + '-' + tmp[1] + '_' + tmp[2]
        replacement = {'%date%': current_date,
                       '%username%': username,
                       '%computer%': computer,
                       '%distribution%': distribution}
        # Mode 'random'.
        self.config.SetMode('random')
        self.config.SetReplacementMap(replacement)
        self.config.Proceed()
        self.assert_(self.config.IsReady())
        # Removes the copy of the configuration file.
        os.remove(self.config.file_list[-1])

        # Mode 'random_path'.
        self.config.SetMode('random_path')
        self.config.SetReplacementMap(replacement)
        self.config.Proceed()
        self.assert_(self.config.IsReady())
        # Removes the copy of the configuration file.
        os.remove(self.config.file_list[-1])
        os.removedirs(os.path.dirname(self.config.file_list[-1]))

        # Mode 'raw'.
        self.config.SetMode('raw')
        self.config.SetPath('/tmp/')
        self.config.SetReplacementMap(replacement)
        self.config.Proceed()
        self.assert_(self.config.IsReady())
        # Removes the copy of the configuration file.
        os.remove(self.config.file_list[-1])




##############
# PROCESSING #
##############

# Processes the tests when you launch this python file.
if __name__ == '__main__':
    # Deletes the modules 'network.py' and 'program_manager'.
    # You don't have to reload 'ipython' for each changement in a module.
    del sys.modules['network']
    del sys.modules['program_manager']
    sys.path.insert(0, '../')
    import network, program_manager
    sys.path.pop(0)

    # Host tests.
    suite_host = unittest.TestLoader()\
        .loadTestsFromTestCase(HostTestCase)
    # Network tests.
    suite_net = unittest.TestLoader()\
        .loadTestsFromTestCase(NetworkTestCase)
    # Program_manager tests.
    suite_program_manager = unittest.TestLoader()\
        .loadTestsFromTestCase(ProgramManagerTestCase)
    # Program tests.
    suite_program = unittest.TestLoader()\
        .loadTestsFromTestCase(ProgramTestCase)
    # Configuration tests.
    suite_configuration = unittest.TestLoader()\
        .loadTestsFromTestCase(ConfigurationTestCase)
    # Tests suite.
    suite = unittest.TestSuite([suite_host, suite_net, suite_program_manager,
                                suite_program, suite_configuration])
    # Runs the tests.
    unittest.TextTestRunner(verbosity = 2).run(suite)

