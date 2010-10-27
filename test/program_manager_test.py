# Copyright (C) 2008-2010 INRIA - EDF R&D
# Author: Damien Garaud
#
# This file is part of the PuppetMaster project. It checks the module
# 'program_manager'.
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
sys.path.insert(0, '../src')
import program_manager
sys.path.pop(0)


#######################
# Class Configuration #
#######################

class ConfigurationTestCase(unittest.TestCase):

    # List of all testing methods.
    _method_name_ = ['testAccessMethods', 'testProcessingMethods']
    # Default path to configuration file.
    _config_file_ = '../example/example.cfg'

    def __init__(self, methodName='runTest', config_file = _config_file_):
        unittest.TestCase.__init__(self, methodName)
        self.config_file = config_file

    def setUp(self):
        # 'Configuration' instance.
        self.config = program_manager.Configuration(self.config_file)
        # Raises an error if the file is not found.
        self.assertRaises(Exception, program_manager.Configuration, 'no_file')

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
        self.assertTrue(self.config.IsReady())
        # Removes the copy of the configuration file.
        os.remove(self.config.file_list[-1])

        # Mode 'random_path'.
        self.config.SetMode('random_path')
        self.config.SetReplacementMap(replacement)
        self.config.Proceed()
        self.assertTrue(self.config.IsReady())
        # Removes the copy of the configuration file.
        os.remove(self.config.file_list[-1])
        os.removedirs(os.path.dirname(self.config.file_list[-1]))

        # Mode 'raw'.
        self.config.SetMode('raw')
        self.config.SetPath('/tmp/')
        self.config.SetReplacementMap(replacement)
        self.config.Proceed()
        self.assertTrue(self.config.IsReady())
        # Removes the copy of the configuration file.
        os.remove(self.config.file_list[-1])


#################
# Class Program #
#################

class ProgramTestCase(unittest.TestCase):

    # List of all testing methods.
    _method_name_ = ['testAccessMethods', 'testProcessingMethods']

    def setUp(self):
        self.command_name = '/bin/ls'
        self.program = program_manager.Program(self.command_name)

    def tearDown(self):
        pass

    def testAccessMethods(self):
        command_name = self.program.Command()
        self.assertTrue(isinstance(command_name, str))

    def testProcessingMethods(self):
        self.assertTrue(self.program.IsReady())
        self.program.Try()
        self.program.Run()


########################
# Class ProgramManager #
########################

class ProgramManagerTestCase(unittest.TestCase):

    # List of all testing methods.
    _method_name_ = ['testInit', 'testAccessMethods',
                     'testProcessingMethods']

    def __init__(self, methodName='runTest', host_file = None):
        unittest.TestCase.__init__(self, methodName)
        self.host_file = host_file
        # If there is file.
        if self.host_file == None:
            self.is_file = False
        else:
            self.is_file = True

    def setUp(self):
        count = 0
        self.delay = 2.
        # Is there a host file?
        if self.is_file:
            network_ = program_manager.network.Network(self.host_file, True)
            self.program_manager = \
                program_manager.ProgramManager(network_)
        else:
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
        self.assertTrue(isinstance(log, str))

    def testProcessingMethods(self):
        self.program_manager.Try()
        self.program_manager.Run()
        self.program_manager.RunNetwork(self.delay)
        self.program_manager.Clear()
        self.assertTrue(len(self.program_manager.program_list) == 0)
