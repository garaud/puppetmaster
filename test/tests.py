# Copyright (C) 2008-2009 EDF R&D
# Author: Damien Garaud
# 
# This file is part of the air quality modeling system Polyphemus. It is used
# to check ensemble generation.
# 
# Polyphemus is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Polyphemus is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# For more information, visit the Polyphemus web site:
#      http://cerea.enpc.fr/polyphemus/

import os, sys
import unittest
sys.path.insert(0, '../')
from ensemble_generation import *
sys.path.pop(0)


####################
# GLOBAL VARIABLES #
####################

# The parameter configuration file.
config_parameter = "../example/parameter.cfg"

# The program configuration file.
config_program = "../example/program.cfg"

# The polyphemus directory.
polyphemus_dir = "../../.."


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


###########################
# ENSEMBLE PARAMETER TEST #
###########################

class EnsembleParameterTest(unittest.TestCase):
    
    def setUp(self):
        # The loop number for the random number generation.
        self.Nloop = 1000

    def testLoadEnsembleParameter(self):
        # Declarations.
        ep = EnsembleParameter()

        # Raises an Exception for a wrong file.
        self.assertRaises(Exception, ep.LoadConfiguration, 'nofile_sorry')
        self.assertRaises(Exception, ep.ReadIdEnsembleFile, 'nofile_sorry',
                          True)
        # An empty ensemble.
        self.assert_(len(ep.id_ensemble) == 0)

        # Equal lengths.
        self.assert_(ep.Nmodel == 0)
        self.assert_(len(ep.value) == len(ep.name))
        self.assert_(len(ep.value) == ep.Nparameter)
        self.assert_(len(ep.name) == ep.Nparameter)
        self.assert_(len(ep.parameter_size) == ep.Nparameter)
        for i in range(ep.Nparameter):
            self.assert_(len(ep.value[i]) == ep.parameter_size[i])
            self.assert_(len(ep.occurrence_frequency[i]) == ep.parameter_size[i])
        
        # Loading.
        ep.LoadConfiguration(config_parameter)
        if len(ep.config.input_data[0]) != 0:
            Ntmp = ep.Nparameter - len(ep.config.input_data)
        else:
            Ntmp = ep.Nparameter

        # Equal lengths.
        self.assert_(len(ep.value) == len(ep.name))
        self.assert_(len(ep.value) == ep.Nparameter)
        self.assert_(len(ep.name) == ep.Nparameter)
        self.assert_(len(ep.parameter_size) == ep.Nparameter)
        self.assert_(len(ep.occurrence_frequency) == Ntmp)
        for i in range(Ntmp):
            self.assert_(len(ep.value[i]) == ep.parameter_size[i])
            self.assert_(len(ep.occurrence_frequency[i]) \
                             == ep.parameter_size[i])

    def testGenerateEnsemble(self):
        import random

        # Declarations.
        ep = EnsembleParameter(config_parameter)
        if len(ep.config.input_data[0]) != 0:
            Ntmp = ep.Nparameter - len(ep.config.input_data)
        else:
            Ntmp = ep.Nparameter

        # Equal lengths.
        self.assert_(len(ep.value) == len(ep.name))
        self.assert_(len(ep.value) == ep.Nparameter)
        self.assert_(len(ep.name) == ep.Nparameter)
        self.assert_(len(ep.parameter_size) == ep.Nparameter)
        self.assert_(len(ep.occurrence_frequency) == Ntmp)
        for i in range(Ntmp):
            self.assert_(len(ep.value[i]) == ep.parameter_size[i])
            self.assert_(len(ep.occurrence_frequency[i]) \
                             == ep.parameter_size[i])

        # Generates an ensemble.
        ep.GenerateIdEnsemble()
        self.assert_(len(ep.id_ensemble) == ep.Nmodel)
        for i in range(ep.Nmodel):
            self.assert_(len(ep.id_ensemble[i]) == ep.Nparameter)

        # Checks the ensemble.
        self.assert_(ep.CheckIdEnsemble())

        # For the random number generation.
        for i in range(self.Nloop):
            index_parameter = random.randint(0, Ntmp - 1)
            choice_list = range(ep.parameter_size[index_parameter])
            index_choice = ep.ParameterChoice(index_parameter)
            self.assert_(index_choice in choice_list)


#########################
# ENSEMBLE PROGRAM TEST #
#########################

class EnsembleProgramTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def testLoadEnsembleProgram(self):
        # Declaration.
        p = EnsembleProgram()

        # Raises an Exception for a wrong file.
        self.assertRaises(Exception, p.Init, 'nofile_sorry', 'nofile_sorry')
        self.assertRaises(Exception, p.ReadIdEnsembleFile, 'nofile_sorry')

        # Loading.
        p.Init(config_parameter, config_program)
        
        # Raises an Exception because the ensemble is empty.
        self.assertRaises(Exception, p.GetGeneralDict, 0)
        p.parameter.GenerateIdEnsemble()

        # Raises an Exception because the 'config_replacement' is not set.
        self.assertRaises(Exception, p.GetGeneralDict, 0)
        
        # Sets the Polyphemus directory.
        p.SetPolyphemusDirectory(polyphemus_dir)

        # Declaration of the ConfigReplacement object.
        config_replacement = modules.ConfigPolair3D()
        p.SetConfigReplacement(config_replacement)

        # Gets the general dictionary for the first model.
        d = p.GetGeneralDict(0)


##############
# PROCESSING #
##############

# Processes the tests when you launch this python file.
if __name__ == '__main__':
    # Deletes the modules from 'ensemble_generation'.
    # You don't have to reload 'ipython' for each changement in a module.
    del sys.modules['ensemble_generation']
    del sys.modules['ensemble_generation.ensemble_parameter']
    del sys.modules['ensemble_generation.ensemble_program']
    del sys.modules['ensemble_generation.function']
    del sys.modules['ensemble_generation.modules']
    del sys.modules['ensemble_generation.network']
    del sys.modules['ensemble_generation.polyphemus']
    sys.path.insert(0, '../')
    from ensemble_generation import *
    sys.path.pop(0)

    # Checks the files and directories.
    if not os.path.isfile(config_parameter):
        raise Exception, "Unable to find the file \"" \
            + config_parameter + "\". Please change it in the file \"" \
            + os.sys.argv[0] + "\"."
    if not os.path.isfile(config_program):
        raise Exception, "Unable to find the file \"" \
            + config_program + "\". Please change it in the file \"" \
            + os.sys.argv[0] + "\"."
    if not os.path.isdir(polyphemus_dir):
        raise Exception, "Unable to find the directory \"" \
            + polyphemus_dir + "\". Please change it in the file \"" \
            + os.sys.argv[0] + "\"."
    
    # Host tests.
    suite_host = unittest.TestLoader()\
        .loadTestsFromTestCase(HostTestCase)
    # Network tests.
    suite_net = unittest.TestLoader()\
        .loadTestsFromTestCase(NetworkTestCase)
    # EnsembleParameter tests.
    suite_parameter = unittest.TestLoader()\
        .loadTestsFromTestCase(EnsembleParameterTest)
    # EnsembleProgram tests.
    suite_program = unittest.TestLoader()\
        .loadTestsFromTestCase(EnsembleProgramTest)
    # TestSuite.
    suite = unittest.TestSuite([suite_host, suite_net, suite_parameter,
                                suite_program])
    unittest.TextTestRunner(verbosity = 2).run(suite)

