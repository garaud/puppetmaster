# Copyright (C) 2008-2010 INRIA - EDF R&D
# Author: Damien Garaud
#
# This file is part of the PuppetMaster project. It checks the module
# 'host', 'network' and 'program_manager'.
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

import os
import sys
import optparse
import unittest

##################
# LOADING MODULE #
##################

# The module names.
__module_name__ = ['host', 'network', 'program_manager']

# Deletes all modules if they are already imported.
# You don't have to reload 'ipython' if a module has changed.
for name in __module_name__:
    if sys.modules.has_key(name):
        del sys.modules[name]

from puppetmaster import host, network, program_manager

# Same operation for test modules.
for name in ['host_test', 'network_test', 'program_manager_test']:
    if sys.modules.has_key(name):
        del sys.modules[name]
import host_test, network_test, program_manager_test


###################
# OPTIONS PARSING #
###################

# Parser instance.
usage = "%prog [options]"
parser = optparse.OptionParser(usage = usage)
parser.add_option("-m", "--module", dest="module_name", default='all',
                  help="The name of the tested module "\
                      +"('all', 'host', 'network' or 'program_manager')."\
                      + " 'all' by default.")
parser.add_option("-f", "--file",
                  help="The name of the file where there are the host names."\
                      + " If it is not given, just tests the local host.",
                  metavar="FILE")
parser.add_option("--force-ssh-config", dest="forced_ssh", action="store_true",
                  default=False,
                  help="Uses the SSH configuration from PuppetMaster.")

(options, args) = parser.parse_args()

# If the number of arguments is wrong.
if len(args) >= 3:
    print "Improper usage!"
    print "Use option -h or --help for information about usage."
    sys.exit(1)


####################
# OPTIONS CHECKING #
####################

# Host list file.
if options.file != None:
    if not os.path.isfile(options.file):
        parser.error("options -f. The file '%s' not found." % options.file)
    host_file = os.path.abspath(options.file)
else:
    host_file = None

# Which module?
if options.module_name not in __module_name__ + ['all']:
    parser.print_help()
    parser.error("options -m. Module '%s' not found." % options.module_name)


###################
# TEST PROCESSING #
###################

# Configuration file for the class 'ProgramManager'.
configuration_file = '../example/example.cfg'
configuration_file = os.path.abspath(configuration_file)

# Which module will be tested.
# All modules.
if options.module_name == 'all':
    suite = unittest.TestSuite()
    # For the module 'host'.
    for method_name in host_test.test_method_name:
        suite.addTest(host_test.HostTestCase(method_name, host_file,
                                             options.forced_ssh))
    # For the module 'network'.
    for method_name in network_test.test_method_name:
        suite.addTest(network_test.NetworkTestCase(method_name, host_file,
                                                   options.forced_ssh))
    # For the module 'program_manager'.
    # Class 'Configuration'.
    config_method_list = \
        program_manager_test.ConfigurationTestCase._method_name_
    for method_name in config_method_list:
        suite.addTest(program_manager_test.\
                          ConfigurationTestCase(method_name,
                                                configuration_file))
    # Class 'Program'.
    program_method_list = program_manager_test.ProgramTestCase._method_name_
    for method_name in program_method_list:
        suite.addTest(program_manager_test.ProgramTestCase(method_name))
    # Class 'ProgramManager'.
    progmanager_method_list = \
        program_manager_test.ProgramManagerTestCase._method_name_
    for method_name in progmanager_method_list:
        suite.addTest(program_manager_test.\
                          ProgramManagerTestCase(method_name,
                                                 host_file,
                                                 options.forced_ssh))
    unittest.TextTestRunner(verbosity=2).run(suite)
# 'host' module.
elif options.module_name == 'host':
    suite = unittest.TestSuite()
    for method_name in host_test.test_method_name:
        suite.addTest(host_test.HostTestCase(method_name, host_file,
                                             options.forced_ssh))
    unittest.TextTestRunner(verbosity=2).run(suite)
# 'network' module.
elif options.module_name == 'network':
    suite = unittest.TestSuite()
    for method_name in network_test.test_method_name:
        suite.addTest(network_test.NetworkTestCase(method_name, host_file,
                                                   options.forced_ssh))
    unittest.TextTestRunner(verbosity=2).run(suite)
# 'program_manager' module.
elif options.module_name == 'program_manager':
    suite = unittest.TestSuite()
    # Class 'Configuration'.
    config_method_list = \
        program_manager_test.ConfigurationTestCase._method_name_
    for method_name in config_method_list:
        suite.addTest(program_manager_test.\
                          ConfigurationTestCase(method_name,
                                                configuration_file))
    # Class 'Program'.
    program_method_list = program_manager_test.ProgramTestCase._method_name_
    for method_name in program_method_list:
        suite.addTest(program_manager_test.ProgramTestCase(method_name))
    # Class 'ProgramManager'.
    progmanager_method_list = \
        program_manager_test.ProgramManagerTestCase._method_name_
    for method_name in progmanager_method_list:
        suite.addTest(program_manager_test.\
                          ProgramManagerTestCase(method_name,
                                                 host_file,
                                                 options.forced_ssh))
    unittest.TextTestRunner(verbosity=2).run(suite)
else:
    parser.help_message()
    raise ValueError, "The option '-m %s' not found." % options.module_name

